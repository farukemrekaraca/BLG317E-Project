from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.schemas.transaction import TransactionCreate, TransactionResponse
from app.db.database import get_db
from app.core.dependencies import get_current_user
import uuid
from datetime import datetime

router = APIRouter()


@router.post("", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(
    transaction: TransactionCreate,
    cursor=Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new transaction (purchase tickets).

    This endpoint handles ticket purchasing by:
    1. Verifying all tickets are available
    2. Creating a transaction record
    3. Updating ticket statuses to 'sold' and assigning owner
    4. Creating transaction items for tracking
    """
    # Verify all tickets exist and are available
    if not transaction.ticket_ids:
        raise HTTPException(status_code=400, detail="No tickets provided")

    placeholders = ','.join(['%s'] * len(transaction.ticket_ids))
    cursor.execute(
        f"""
        SELECT ticket_id, status FROM tickets
        WHERE ticket_id IN ({placeholders})
        """,
        transaction.ticket_ids
    )
    tickets = cursor.fetchall()

    if len(tickets) != len(transaction.ticket_ids):
        raise HTTPException(status_code=404, detail="One or more tickets not found")

    # Check if all tickets are available
    unavailable = [t['ticket_id'] for t in tickets if t['status'] != 'available']
    if unavailable:
        raise HTTPException(
            status_code=400,
            detail=f"Tickets {unavailable} are not available for purchase"
        )

    # Generate unique receipt ID
    receipt_id = f"TFR{uuid.uuid4().hex[:12].upper()}"

    # Create transaction
    cursor.execute(
        """
        INSERT INTO transactions (user_id, date, price, payment_method, receipt_id, installment_period)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING transaction_id, user_id, date, price, payment_method, receipt_id, installment_period
        """,
        (current_user["user_id"], datetime.utcnow(), transaction.price,
         transaction.payment_method, receipt_id, transaction.installment_period)
    )
    new_transaction = cursor.fetchone()

    # Update tickets to sold and assign owner
    cursor.execute(
        f"""
        UPDATE tickets
        SET status = 'sold', owner_id = %s
        WHERE ticket_id IN ({placeholders})
        """,
        [current_user["user_id"]] + transaction.ticket_ids
    )

    # Create transaction items
    for ticket_id in transaction.ticket_ids:
        cursor.execute(
            "INSERT INTO transaction_items (ticket_id, transaction_id) VALUES (%s, %s)",
            (ticket_id, new_transaction["transaction_id"])
        )

    return dict(new_transaction)


@router.get("", response_model=List[TransactionResponse])
def get_transactions(
    cursor=Depends(get_db),
    current_user: dict = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
):
    """Get all transactions for the current user"""
    cursor.execute(
        """
        SELECT transaction_id, user_id, date, price, payment_method, receipt_id, installment_period
        FROM transactions
        WHERE user_id = %s
        ORDER BY date DESC
        LIMIT %s OFFSET %s
        """,
        (current_user["user_id"], limit, skip)
    )
    transactions = cursor.fetchall()
    return [dict(t) for t in transactions]


@router.get("/all", response_model=List[TransactionResponse])
def get_all_transactions(
    cursor=Depends(get_db),
    current_user: dict = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
):
    """Get all transactions (Admin only)"""
    # Check if user is admin
    cursor.execute(
        """
        SELECT authorization_level FROM user_type ut
        JOIN users u ON ut.user_type_id = u.type_id
        WHERE u.user_id = %s
        """,
        (current_user["user_id"],)
    )
    user_auth = cursor.fetchone()

    if not user_auth or user_auth["authorization_level"] < 3:
        raise HTTPException(status_code=403, detail="Not authorized")

    cursor.execute(
        """
        SELECT transaction_id, user_id, date, price, payment_method, receipt_id, installment_period
        FROM transactions
        ORDER BY date DESC
        LIMIT %s OFFSET %s
        """,
        (limit, skip)
    )
    transactions = cursor.fetchall()
    return [dict(t) for t in transactions]


@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(
    transaction_id: int,
    cursor=Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a specific transaction by ID"""
    cursor.execute(
        """
        SELECT transaction_id, user_id, date, price, payment_method, receipt_id, installment_period
        FROM transactions
        WHERE transaction_id = %s
        """,
        (transaction_id,)
    )
    transaction = cursor.fetchone()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    # Check if user owns this transaction or is admin
    cursor.execute(
        """
        SELECT authorization_level FROM user_type ut
        JOIN users u ON ut.user_type_id = u.type_id
        WHERE u.user_id = %s
        """,
        (current_user["user_id"],)
    )
    user_auth = cursor.fetchone()

    if transaction["user_id"] != current_user["user_id"] and user_auth["authorization_level"] < 3:
        raise HTTPException(status_code=403, detail="Not authorized to view this transaction")

    return dict(transaction)


@router.get("/{transaction_id}/items")
def get_transaction_items(
    transaction_id: int,
    cursor=Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all items (tickets) in a transaction"""
    # Verify transaction exists and user has access
    cursor.execute(
        "SELECT user_id FROM transactions WHERE transaction_id = %s",
        (transaction_id,)
    )
    transaction = cursor.fetchone()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    # Check authorization
    cursor.execute(
        """
        SELECT authorization_level FROM user_type ut
        JOIN users u ON ut.user_type_id = u.type_id
        WHERE u.user_id = %s
        """,
        (current_user["user_id"],)
    )
    user_auth = cursor.fetchone()

    if transaction["user_id"] != current_user["user_id"] and user_auth["authorization_level"] < 3:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Get transaction items
    cursor.execute(
        """
        SELECT ti.ticket_id, ti.transaction_id, t.seat_id, t.ticket_type_id, t.status
        FROM transaction_items ti
        JOIN tickets t ON ti.ticket_id = t.ticket_id
        WHERE ti.transaction_id = %s
        """,
        (transaction_id,)
    )
    items = cursor.fetchall()
    return [dict(item) for item in items]
