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
    current_user: dict = Depends(require_role(2))  # Venue Owner or above
):
    """Create a new venue (Venue Owner/Organizer/Admin only)"""
    cursor.execute(
        """
        INSERT INTO venues (owner_id, name, country, city, address, media_url, website_url, seat_count, section_count)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING venue_id, owner_id, name, country, city, address, media_url, website_url, seat_count, section_count
        """,
        (current_user["user_id"], venue.name, venue.country, venue.city, venue.address,
         venue.media_url, venue.website_url, venue.seat_count, venue.section_count)
    )
    new_venue = cursor.fetchone()
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
    current_user: dict = Depends(require_role(2))
):
    """Update a venue (only by the owner who created it or admin)"""
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

    # Build update query
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
    if venue_update.seat_count is not None:
        update_fields.append("seat_count = %s")
        update_values.append(venue_update.seat_count)
    if venue_update.section_count is not None:
        update_fields.append("section_count = %s")
        update_values.append(venue_update.section_count)

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
