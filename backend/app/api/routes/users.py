from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.schemas.user import UserResponse
from app.db.database import get_db
from app.core.dependencies import get_current_user, require_role

router = APIRouter()


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: dict = Depends(get_current_user), cursor=Depends(get_db)):
    """Get current authenticated user's information"""
    cursor.execute(
        """
        SELECT user_id, type_id, name, mail_address, phone_number, created_at
        FROM users
        WHERE user_id = %s
        """,
        (current_user["user_id"],)
    )
    user = cursor.fetchone()
    return dict(user)


@router.get("", response_model=List[UserResponse])
def get_users(
    skip: int = 0,
    limit: int = 100,
    cursor=Depends(get_db),
    current_user: dict = Depends(require_role(3))  # Admin only
):
    """Get all users (Admin only)"""
    cursor.execute(
        """
        SELECT user_id, type_id, name, mail_address, phone_number, created_at
        FROM users
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
        """,
        (limit, skip)
    )
    users = cursor.fetchall()
    return [dict(u) for u in users]


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    cursor=Depends(get_db),
    current_user: dict = Depends(require_role(3))  # Admin only
):
    """Get a specific user by ID (Admin only)"""
    cursor.execute(
        """
        SELECT user_id, type_id, name, mail_address, phone_number, created_at
        FROM users
        WHERE user_id = %s
        """,
        (user_id,)
    )
    user = cursor.fetchone()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return dict(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    cursor=Depends(get_db),
    current_user: dict = Depends(require_role(3))  # Admin only
):
    """Delete a user (Admin only)"""
    # Prevent deleting yourself
    if user_id == current_user["user_id"]:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")

    cursor.execute("DELETE FROM users WHERE user_id = %s RETURNING user_id", (user_id,))
    deleted = cursor.fetchone()
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return None


@router.get("/me/tickets")
def get_my_tickets(
    cursor=Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all tickets owned by the current user"""
    cursor.execute(
        """
        SELECT t.ticket_id, t.seat_id, t.ticket_type_id, t.status,
               tt.name as ticket_type_name, tt.price,
               e.event_id, e.name as event_name, e.date as event_date,
               v.name as venue_name, v.city as venue_city
        FROM tickets t
        JOIN ticket_type tt ON t.ticket_type_id = tt.ticket_type_id
        JOIN events e ON tt.event_id = e.event_id
        JOIN venues v ON e.venue_id = v.venue_id
        WHERE t.owner_id = %s
        ORDER BY e.date
        """,
        (current_user["user_id"],)
    )
    tickets = cursor.fetchall()
    return [dict(ticket) for ticket in tickets]
