from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.schemas.ticket import TicketCreate, TicketUpdate, TicketResponse, TicketTypeCreate, TicketTypeResponse
from app.db.database import get_db
from app.core.dependencies import get_current_user, require_role

router = APIRouter()


# Ticket Type Endpoints
@router.post("/types", response_model=TicketTypeResponse, status_code=status.HTTP_201_CREATED)
def create_ticket_type(
    ticket_type: TicketTypeCreate,
    cursor=Depends(get_db),
    current_user: dict = Depends(require_role(2))  # Organizer or above
):
    """Create a new ticket type for an event (Organizer only)"""
    # Verify event exists
    cursor.execute("SELECT event_id FROM events WHERE event_id = %s", (ticket_type.event_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Event not found")

    cursor.execute(
        """
        INSERT INTO ticket_type (event_id, name, price)
        VALUES (%s, %s, %s)
        RETURNING ticket_type_id, event_id, name, price
        """,
        (ticket_type.event_id, ticket_type.name, ticket_type.price)
    )
    new_type = cursor.fetchone()
    return dict(new_type)


@router.get("/types", response_model=List[TicketTypeResponse])
def get_ticket_types(event_id: int = None, cursor=Depends(get_db)):
    """Get all ticket types, optionally filtered by event"""
    if event_id:
        cursor.execute(
            "SELECT ticket_type_id, event_id, name, price FROM ticket_type WHERE event_id = %s",
            (event_id,)
        )
    else:
        cursor.execute("SELECT ticket_type_id, event_id, name, price FROM ticket_type")

    types = cursor.fetchall()
    return [dict(t) for t in types]


# Ticket Endpoints
@router.post("", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
def create_ticket(
    ticket: TicketCreate,
    cursor=Depends(get_db),
    current_user: dict = Depends(require_role(2))  # Organizer or above
):
    """Create a new ticket (Organizer only)"""
    # Verify seat exists
    cursor.execute("SELECT seat_id FROM seats WHERE seat_id = %s", (ticket.seat_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Seat not found")

    # Verify ticket type exists
    cursor.execute("SELECT ticket_type_id FROM ticket_type WHERE ticket_type_id = %s", (ticket.ticket_type_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Ticket type not found")

    cursor.execute(
        """
        INSERT INTO tickets (seat_id, ticket_type_id, status)
        VALUES (%s, %s, %s)
        RETURNING ticket_id, seat_id, owner_id, ticket_type_id, status
        """,
        (ticket.seat_id, ticket.ticket_type_id, ticket.status)
    )
    new_ticket = cursor.fetchone()
    return dict(new_ticket)


@router.get("", response_model=List[TicketResponse])
def get_tickets(
    event_id: int = None,
    status_filter: str = None,
    skip: int = 0,
    limit: int = 100,
    cursor=Depends(get_db)
):
    """Get all tickets with optional filtering"""
    query = """
        SELECT t.ticket_id, t.seat_id, t.owner_id, t.ticket_type_id, t.status
        FROM tickets t
    """
    conditions = []
    params = []

    if event_id:
        query += " JOIN ticket_type tt ON t.ticket_type_id = tt.ticket_type_id"
        conditions.append("tt.event_id = %s")
        params.append(event_id)

    if status_filter:
        conditions.append("t.status = %s")
        params.append(status_filter)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY t.ticket_id LIMIT %s OFFSET %s"
    params.extend([limit, skip])

    cursor.execute(query, params)
    tickets = cursor.fetchall()
    return [dict(t) for t in tickets]


@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(ticket_id: int, cursor=Depends(get_db)):
    """Get a specific ticket by ID"""
    cursor.execute(
        """
        SELECT ticket_id, seat_id, owner_id, ticket_type_id, status
        FROM tickets
        WHERE ticket_id = %s
        """,
        (ticket_id,)
    )
    ticket = cursor.fetchone()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return dict(ticket)


@router.put("/{ticket_id}", response_model=TicketResponse)
def update_ticket(
    ticket_id: int,
    ticket_update: TicketUpdate,
    cursor=Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update a ticket (status/owner)"""
    # Check if ticket exists
    cursor.execute("SELECT ticket_id, status FROM tickets WHERE ticket_id = %s", (ticket_id,))
    ticket = cursor.fetchone()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # Build update query
    update_fields = []
    update_values = []

    if ticket_update.owner_id is not None:
        update_fields.append("owner_id = %s")
        update_values.append(ticket_update.owner_id)

    if ticket_update.status is not None:
        if ticket_update.status not in ['available', 'reserved', 'sold']:
            raise HTTPException(status_code=400, detail="Invalid status")
        update_fields.append("status = %s")
        update_values.append(ticket_update.status)

    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update")

    update_values.append(ticket_id)
    query = f"""
        UPDATE tickets SET {', '.join(update_fields)}
        WHERE ticket_id = %s
        RETURNING ticket_id, seat_id, owner_id, ticket_type_id, status
    """

    cursor.execute(query, update_values)
    updated_ticket = cursor.fetchone()
    return dict(updated_ticket)


@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ticket(
    ticket_id: int,
    cursor=Depends(get_db),
    current_user: dict = Depends(require_role(3))  # Admin only
):
    """Delete a ticket (Admin only)"""
    cursor.execute("DELETE FROM tickets WHERE ticket_id = %s RETURNING ticket_id", (ticket_id,))
    deleted = cursor.fetchone()
    if not deleted:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return None
