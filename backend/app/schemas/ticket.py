from pydantic import BaseModel
from typing import Optional


class TicketBase(BaseModel):
    seat_id: int
    ticket_type_id: int
    status: str = "available"


class TicketCreate(TicketBase):
    pass


class TicketUpdate(BaseModel):
    owner_id: Optional[int] = None
    status: Optional[str] = None


class TicketResponse(TicketBase):
    ticket_id: int
    owner_id: Optional[int] = None

    class Config:
        from_attributes = True


class TicketTypeBase(BaseModel):
    event_id: int
    name: str
    price: float


class TicketTypeCreate(TicketTypeBase):
    pass


class TicketTypeResponse(TicketTypeBase):
    ticket_type_id: int

    class Config:
        from_attributes = True
