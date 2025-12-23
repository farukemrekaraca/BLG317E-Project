from pydantic import BaseModel
from typing import Optional
from datetime import date


class EventBase(BaseModel):
    name: str
    date: date
    venue_id: int
    event_type_id: int


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    name: Optional[str] = None
    date: Optional[date] = None
    venue_id: Optional[int] = None
    event_type_id: Optional[int] = None


class EventResponse(EventBase):
    event_id: int
    organizer_id: int

    class Config:
        from_attributes = True


class EventTypeBase(BaseModel):
    name: str


class EventTypeCreate(EventTypeBase):
    pass


class EventTypeResponse(EventTypeBase):
    event_type_id: int

    class Config:
        from_attributes = True
