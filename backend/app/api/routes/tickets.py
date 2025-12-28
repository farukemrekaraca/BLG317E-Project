from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.schemas.ticket import (
    TicketCreate, TicketUpdate, TicketResponse,
    TicketTypeCreate, TicketTypeResponse,
    SectionTicketTypeMapping, BulkTicketGenerateRequest, BulkTicketGenerateResponse,
    EventBulkGenerateRequest, EventBulkGenerateResponse
)
from app.db.database import get_db
from app.core.dependencies import get_current_user, require_role

router = APIRouter()


# Ticket Type Endpoints
@router.post("/types", response_model=TicketTypeResponse, status_code=status.HTTP_201_CREATED)
def create_ticket_type(
    ticket_type: TicketTypeCreate,
    cursor=Depends(get_db),
    current_user: dict = Depends(require_role(1))  # Organizer or above
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
    current_user: dict = Depends(require_role(1))  # Organizer or above
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


# Section-Ticket Type Mapping Endpoints
@router.post("/mappings", response_model=SectionTicketTypeMapping, status_code=status.HTTP_201_CREATED)
def create_section_ticket_mapping(
    mapping: SectionTicketTypeMapping,
    cursor=Depends(get_db),
    current_user: dict = Depends(require_role(1))  # Organizer or above
):
    """Create a mapping between a section and ticket type (Organizer only)"""
    # Verify section exists
    cursor.execute("SELECT section_id FROM sections WHERE section_id = %s", (mapping.section_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Section not found")

    # Verify ticket type exists
    cursor.execute("SELECT ticket_type_id FROM ticket_type WHERE ticket_type_id = %s", (mapping.ticket_type_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Ticket type not found")

    # Check if mapping already exists
    cursor.execute(
        "SELECT * FROM section_ticket_type_mapping WHERE section_id = %s AND ticket_type_id = %s",
        (mapping.section_id, mapping.ticket_type_id)
    )
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="Mapping already exists")

    # Create mapping
    cursor.execute(
        """
        INSERT INTO section_ticket_type_mapping (section_id, ticket_type_id)
        VALUES (%s, %s)
        RETURNING section_id, ticket_type_id
        """,
        (mapping.section_id, mapping.ticket_type_id)
    )
    new_mapping = cursor.fetchone()
    return dict(new_mapping)


@router.get("/mappings", response_model=List[SectionTicketTypeMapping])
def get_section_ticket_mappings(
    section_id: int = None,
    ticket_type_id: int = None,
    cursor=Depends(get_db)
):
    """Get all section-ticket type mappings with optional filtering"""
    query = "SELECT section_id, ticket_type_id FROM section_ticket_type_mapping"
    conditions = []
    params = []

    if section_id:
        conditions.append("section_id = %s")
        params.append(section_id)

    if ticket_type_id:
        conditions.append("ticket_type_id = %s")
        params.append(ticket_type_id)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    cursor.execute(query, params)
    mappings = cursor.fetchall()
    return [dict(m) for m in mappings]


@router.delete("/mappings", status_code=status.HTTP_204_NO_CONTENT)
def delete_section_ticket_mapping(
    section_id: int,
    ticket_type_id: int,
    cursor=Depends(get_db),
    current_user: dict = Depends(require_role(1))  # Organizer or above
):
    """Delete a section-ticket type mapping (Organizer only)"""
    cursor.execute(
        """
        DELETE FROM section_ticket_type_mapping
        WHERE section_id = %s AND ticket_type_id = %s
        RETURNING section_id
        """,
        (section_id, ticket_type_id)
    )
    deleted = cursor.fetchone()
    if not deleted:
        raise HTTPException(status_code=404, detail="Mapping not found")
    return None


# Bulk Ticket Generation
@router.post("/bulk-generate", response_model=BulkTicketGenerateResponse, status_code=status.HTTP_201_CREATED)
def bulk_generate_tickets(
    request: BulkTicketGenerateRequest,
    cursor=Depends(get_db),
    current_user: dict = Depends(require_role(1))  # Organizer or above
):
    """
    Automatically generate tickets for all seats in a section with a specific ticket type.

    This endpoint:
    1. Validates that the section-ticket type mapping exists
    2. Gets all seats in the section
    3. Creates tickets for seats that don't already have one for this ticket type
    4. Returns the count of tickets created
    """
    # Verify the section-ticket type mapping exists
    cursor.execute(
        """
        SELECT * FROM section_ticket_type_mapping
        WHERE section_id = %s AND ticket_type_id = %s
        """,
        (request.section_id, request.ticket_type_id)
    )
    if not cursor.fetchone():
        raise HTTPException(
            status_code=404,
            detail="Section-ticket type mapping not found. Create the mapping first."
        )

    # Get all seats in the section
    cursor.execute(
        "SELECT seat_id FROM seats WHERE section_id = %s",
        (request.section_id,)
    )
    seats = cursor.fetchall()

    if not seats:
        raise HTTPException(status_code=404, detail="No seats found in this section")

    # For each seat, create a ticket if one doesn't already exist for this ticket type
    tickets_created = 0
    for seat in seats:
        seat_id = seat['seat_id']

        # Check if a ticket already exists for this seat and ticket type
        cursor.execute(
            """
            SELECT ticket_id FROM tickets
            WHERE seat_id = %s AND ticket_type_id = %s
            """,
            (seat_id, request.ticket_type_id)
        )

        if not cursor.fetchone():
            # Create the ticket
            cursor.execute(
                """
                INSERT INTO tickets (seat_id, ticket_type_id, status)
                VALUES (%s, %s, 'available')
                """,
                (seat_id, request.ticket_type_id)
            )
            tickets_created += 1

    return {
        "tickets_created": tickets_created,
        "section_id": request.section_id,
        "ticket_type_id": request.ticket_type_id,
        "message": f"Successfully created {tickets_created} tickets for section {request.section_id}"
    }


@router.post("/bulk-generate-event", response_model=EventBulkGenerateResponse, status_code=status.HTTP_201_CREATED)
def bulk_generate_tickets_for_event(
    request: EventBulkGenerateRequest,
    cursor=Depends(get_db),
    current_user: dict = Depends(require_role(1))  # Organizer or above
):
    """
    Automatically generate all tickets for an event.

    This endpoint:
    1. Finds all ticket types for the event
    2. For each ticket type, finds all section mappings
    3. Generates tickets for all seats in each mapped section
    4. Returns total tickets created and mappings processed

    This is the most convenient way to generate all tickets for an event in one API call.
    """
    # Verify event exists
    cursor.execute("SELECT event_id FROM events WHERE event_id = %s", (request.event_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Event not found")

    # Get all ticket types for this event
    cursor.execute(
        "SELECT ticket_type_id FROM ticket_type WHERE event_id = %s",
        (request.event_id,)
    )
    ticket_types = cursor.fetchall()

    if not ticket_types:
        raise HTTPException(
            status_code=404,
            detail="No ticket types found for this event. Create ticket types first."
        )

    total_tickets_created = 0
    mappings_processed = 0

    # For each ticket type, find all section mappings and generate tickets
    for ticket_type in ticket_types:
        ticket_type_id = ticket_type['ticket_type_id']

        # Get all section mappings for this ticket type
        cursor.execute(
            """
            SELECT section_id FROM section_ticket_type_mapping
            WHERE ticket_type_id = %s
            """,
            (ticket_type_id,)
        )
        sections = cursor.fetchall()

        # For each section, generate tickets for all seats
        for section in sections:
            section_id = section['section_id']
            mappings_processed += 1

            # Get all seats in this section
            cursor.execute(
                "SELECT seat_id FROM seats WHERE section_id = %s",
                (section_id,)
            )
            seats = cursor.fetchall()

            # Create tickets for seats that don't already have one
            for seat in seats:
                seat_id = seat['seat_id']

                # Check if ticket already exists
                cursor.execute(
                    """
                    SELECT ticket_id FROM tickets
                    WHERE seat_id = %s AND ticket_type_id = %s
                    """,
                    (seat_id, ticket_type_id)
                )

                if not cursor.fetchone():
                    # Create the ticket
                    cursor.execute(
                        """
                        INSERT INTO tickets (seat_id, ticket_type_id, status)
                        VALUES (%s, %s, 'available')
                        """,
                        (seat_id, ticket_type_id)
                    )
                    total_tickets_created += 1

    if mappings_processed == 0:
        raise HTTPException(
            status_code=404,
            detail="No section-ticket type mappings found for this event. Create mappings first."
        )

    return {
        "tickets_created": total_tickets_created,
        "event_id": request.event_id,
        "mappings_processed": mappings_processed,
        "message": f"Successfully created {total_tickets_created} tickets across {mappings_processed} section-ticket type mappings for event {request.event_id}"
    }


# Individual Ticket Endpoints (parameterized routes must come last)
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
