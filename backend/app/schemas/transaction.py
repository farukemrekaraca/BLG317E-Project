from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class TransactionBase(BaseModel):
    price: float
    payment_method: str
    installment_period: Optional[int] = None


class TransactionCreate(TransactionBase):
    ticket_ids: List[int]  # List of ticket IDs to purchase


class TransactionResponse(TransactionBase):
    transaction_id: int
    user_id: int
    date: datetime
    receipt_id: str

    class Config:
        from_attributes = True
