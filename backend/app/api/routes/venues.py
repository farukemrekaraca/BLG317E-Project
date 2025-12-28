from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.schemas.venue import VenueCreate, VenueUpdate, VenueResponse
from app.db.database import get_db
from app.core.dependencies import get_current_user, require_role

router = APIRouter()


@router.post("", response_model=VenueResponse, status_code=status.HTTP_201_CREATED)
def create_venue(
    venue: VenueCreate,
    cursor=Depends(get_db),
    current_user: dict = Depends(require_role(2))  # Venue Owner or Admin only
):
    """
    Create a new venue with automatic section and seat generation (Venue Owner or Admin only).

    This endpoint:
    1. Validates that total seats across sections doesn't exceed venue seat_count
    2. Creates the venue record
    3. For each section configuration:
       - Creates a section with the prefix as the name
       - Creates seats with names like "{prefix}1", "{prefix}2", etc.
    """
    # Validate that total section seats don't exceed venue capacity
    total_section_seats = sum(section.seat_count for section in venue.sections)
    if total_section_seats > venue.seat_count:
        raise HTTPException(
            status_code=400,
            detail=f"Total seats across sections ({total_section_seats}) exceeds venue capacity ({venue.seat_count})"
        )

    # Create the venue
    section_count = len(venue.sections)
    cursor.execute(
        """
        INSERT INTO venues (owner_id, name, country, city, address, media_url, website_url, seat_count, section_count)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING venue_id, owner_id, name, country, city, address, media_url, website_url, seat_count, section_count
        """,
        (current_user["user_id"], venue.name, venue.country, venue.city, venue.address,
         venue.media_url, venue.website_url, venue.seat_count, section_count)
    )
    new_venue = cursor.fetchone()
    venue_id = new_venue["venue_id"]

    # Create sections and seats
    for section_config in venue.sections:
        # Create the section
        cursor.execute(
            """
            INSERT INTO sections (venue_id, name)
            VALUES (%s, %s)
            RETURNING section_id
            """,
            (venue_id, section_config.prefix)
        )
        section = cursor.fetchone()
        section_id = section["section_id"]

        # Create seats for this section
        for seat_number in range(1, section_config.seat_count + 1):
            seat_name = f"{section_config.prefix}{seat_number}"
            cursor.execute(
                """
                INSERT INTO seats (section_id, name)
                VALUES (%s, %s)
                """,
                (section_id, seat_name)
            )

    return dict(new_venue)


@router.get("", response_model=List[VenueResponse])
def get_venues(
    skip: int = 0,
    limit: int = 100,
    city: str = None,
    cursor=Depends(get_db)
):
    """Get all venues with optional filtering by city"""
    if city:
        cursor.execute(
            """
            SELECT venue_id, owner_id, name, country, city, address, media_url, website_url, seat_count, section_count
            FROM venues
            WHERE city = %s
            ORDER BY name
            LIMIT %s OFFSET %s
            """,
            (city, limit, skip)
        )
    else:
        cursor.execute(
            """
            SELECT venue_id, owner_id, name, country, city, address, media_url, website_url, seat_count, section_count
            FROM venues
            ORDER BY name
            LIMIT %s OFFSET %s
            """,
            (limit, skip)
        )
    venues = cursor.fetchall()
    return [dict(v) for v in venues]


@router.get("/{venue_id}", response_model=VenueResponse)
def get_venue(venue_id: int, cursor=Depends(get_db)):
    """Get a specific venue by ID"""
    cursor.execute(
        """
        SELECT venue_id, owner_id, name, country, city, address, media_url, website_url, seat_count, section_count
        FROM venues
        WHERE venue_id = %s
        """,
        (venue_id,)
    )
    venue = cursor.fetchone()
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found")
    return dict(venue)


@router.put("/{venue_id}", response_model=VenueResponse)
def update_venue(
    venue_id: int,
    venue_update: VenueUpdate,
    cursor=Depends(get_db),
    current_user: dict = Depends(require_role(2))  # Venue Owner or Admin only
):
    """
    Update venue metadata only (Venue Owner or Admin).

    Note: Venue structure (seat_count, section_count, sections, seats) cannot be changed after creation.
    Only metadata like name, location, and URLs can be updated.
    Only the venue owner or admin can update venues.
    """
    # Check if venue exists and user is the owner
    cursor.execute("SELECT owner_id FROM venues WHERE venue_id = %s", (venue_id,))
    venue = cursor.fetchone()
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found")

    # Check authorization
    cursor.execute(
        "SELECT authorization_level FROM user_type ut JOIN users u ON ut.user_type_id = u.type_id WHERE u.user_id = %s",
        (current_user["user_id"],)
    )
    user_auth = cursor.fetchone()

    if venue["owner_id"] != current_user["user_id"] and user_auth["authorization_level"] < 3:
        raise HTTPException(status_code=403, detail="Not authorized to update this venue")

    # Build update query (only metadata fields, not structure)
    update_fields = []
    update_values = []

    if venue_update.name is not None:
        update_fields.append("name = %s")
        update_values.append(venue_update.name)
    if venue_update.country is not None:
        update_fields.append("country = %s")
        update_values.append(venue_update.country)
    if venue_update.city is not None:
        update_fields.append("city = %s")
        update_values.append(venue_update.city)
    if venue_update.address is not None:
        update_fields.append("address = %s")
        update_values.append(venue_update.address)
    if venue_update.media_url is not None:
        update_fields.append("media_url = %s")
        update_values.append(venue_update.media_url)
    if venue_update.website_url is not None:
        update_fields.append("website_url = %s")
        update_values.append(venue_update.website_url)

    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update")

    update_values.append(venue_id)
    query = f"""
        UPDATE venues SET {', '.join(update_fields)}
        WHERE venue_id = %s
        RETURNING venue_id, owner_id, name, country, city, address, media_url, website_url, seat_count, section_count
    """

    cursor.execute(query, update_values)
    updated_venue = cursor.fetchone()
    return dict(updated_venue)


@router.delete("/{venue_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_venue(
    venue_id: int,
    cursor=Depends(get_db),
    current_user: dict = Depends(require_role(3))  # Admin only
):
    """Delete a venue (Admin only)"""
    cursor.execute("DELETE FROM venues WHERE venue_id = %s RETURNING venue_id", (venue_id,))
    deleted = cursor.fetchone()
    if not deleted:
        raise HTTPException(status_code=404, detail="Venue not found")
    return None
