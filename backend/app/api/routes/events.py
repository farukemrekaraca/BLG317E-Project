from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.schemas.event import EventCreate, EventUpdate, EventResponse, EventTypeCreate, EventTypeResponse
from app.db.database import get_db
from app.core.dependencies import get_current_user, require_role

router = APIRouter()


# Event Type Endpoints
@router.post("/types", response_model=EventTypeResponse, status_code=status.HTTP_201_CREATED)
def create_event_type(
    event_type: EventTypeCreate,
    cursor=Depends(get_db),
    current_user: dict = Depends(require_role(2))  # Organizer or above
):
    """Create a new event type (Admin/Organizer only)"""
    cursor.execute(
        "INSERT INTO event_type (name) VALUES (%s) RETURNING event_type_id, name",
        (event_type.name,)
    )
    new_type = cursor.fetchone()
    return dict(new_type)


@router.get("/types", response_model=List[EventTypeResponse])
def get_event_types(cursor=Depends(get_db)):
    """Get all event types"""
    cursor.execute("SELECT event_type_id, name FROM event_type ORDER BY name")
    types = cursor.fetchall()
    return [dict(t) for t in types]


@router.get("/types/{event_type_id}", response_model=EventTypeResponse)
def get_event_type(event_type_id: int, cursor=Depends(get_db)):
    """Get a specific event type by ID"""
    cursor.execute(
        "SELECT event_type_id, name FROM event_type WHERE event_type_id = %s",
        (event_type_id,)
    )
    event_type = cursor.fetchone()
    if not event_type:
        raise HTTPException(status_code=404, detail="Event type not found")
    return dict(event_type)


# Event Endpoints
@router.post("", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(
    event: EventCreate,
    cursor=Depends(get_db),
    current_user: dict = Depends(require_role(2))  # Organizer or above
):
    """Create a new event (Organizer only)"""
    # Verify venue exists
    cursor.execute("SELECT venue_id FROM venues WHERE venue_id = %s", (event.venue_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Venue not found")

    # Verify event type exists
    cursor.execute("SELECT event_type_id FROM event_type WHERE event_type_id = %s", (event.event_type_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Event type not found")

    # Insert event
    cursor.execute(
        """
        INSERT INTO events (organizer_id, venue_id, event_type_id, name, date)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING event_id, organizer_id, venue_id, event_type_id, name, date
        """,
        (current_user["user_id"], event.venue_id, event.event_type_id, event.name, event.date)
    )
    new_event = cursor.fetchone()
    return dict(new_event)


@router.get("", response_model=List[EventResponse])
def get_events(
    skip: int = 0,
    limit: int = 100,
    cursor=Depends(get_db)
):
    """Get all events with pagination"""
    cursor.execute(
        """
        SELECT event_id, organizer_id, venue_id, event_type_id, name, date
        FROM events
        ORDER BY date DESC
        LIMIT %s OFFSET %s
        """,
        (limit, skip)
    )
    events = cursor.fetchall()
    return [dict(e) for e in events]


@router.get("/{event_id}", response_model=EventResponse)
def get_event(event_id: int, cursor=Depends(get_db)):
    """Get a specific event by ID"""
    cursor.execute(
        """
        SELECT event_id, organizer_id, venue_id, event_type_id, name, date
        FROM events
        WHERE event_id = %s
        """,
        (event_id,)
    )
    event = cursor.fetchone()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return dict(event)


@router.put("/{event_id}", response_model=EventResponse)
def update_event(
    event_id: int,
    event_update: EventUpdate,
    cursor=Depends(get_db),
    current_user: dict = Depends(require_role(2))  # Organizer or above
):
    """Update an event (only by the organizer who created it)"""
    # Check if event exists and user is the organizer
    cursor.execute(
        "SELECT organizer_id FROM events WHERE event_id = %s",
        (event_id,)
    )
    event = cursor.fetchone()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Check if user is the organizer or admin
    cursor.execute(
        "SELECT authorization_level FROM user_type ut JOIN users u ON ut.user_type_id = u.type_id WHERE u.user_id = %s",
        (current_user["user_id"],)
    )
    user_auth = cursor.fetchone()

    if event["organizer_id"] != current_user["user_id"] and user_auth["authorization_level"] < 3:
        raise HTTPException(status_code=403, detail="Not authorized to update this event")

    # Build update query dynamically
    update_fields = []
    update_values = []

    if event_update.name is not None:
        update_fields.append("name = %s")
        update_values.append(event_update.name)
    if event_update.date is not None:
        update_fields.append("date = %s")
        update_values.append(event_update.date)
    if event_update.venue_id is not None:
        update_fields.append("venue_id = %s")
        update_values.append(event_update.venue_id)
    if event_update.event_type_id is not None:
        update_fields.append("event_type_id = %s")
        update_values.append(event_update.event_type_id)

    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update")

    update_values.append(event_id)
    query = f"UPDATE events SET {', '.join(update_fields)} WHERE event_id = %s RETURNING event_id, organizer_id, venue_id, event_type_id, name, date"

    cursor.execute(query, update_values)
    updated_event = cursor.fetchone()
    return dict(updated_event)


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(
    event_id: int,
    cursor=Depends(get_db),
    current_user: dict = Depends(require_role(2))  # Organizer or above
):
    """Delete an event (Organizer can delete own events, Admin can delete any)"""
    # Check if event exists and get organizer_id
    cursor.execute(
        "SELECT organizer_id FROM events WHERE event_id = %s",
        (event_id,)
    )
    event = cursor.fetchone()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Check if user is the organizer or admin
    cursor.execute(
        "SELECT authorization_level FROM user_type ut JOIN users u ON ut.user_type_id = u.type_id WHERE u.user_id = %s",
        (current_user["user_id"],)
    )
    user_auth = cursor.fetchone()

    # Only allow if user is the organizer or is an admin (auth_level >= 3)
    if event["organizer_id"] != current_user["user_id"] and user_auth["authorization_level"] < 3:
        raise HTTPException(status_code=403, detail="Not authorized to delete this event")

    cursor.execute("DELETE FROM events WHERE event_id = %s RETURNING event_id", (event_id,))
    deleted = cursor.fetchone()
    return None
