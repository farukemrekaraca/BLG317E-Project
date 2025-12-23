from pydantic import BaseModel
from typing import Optional


class VenueBase(BaseModel):
    name: str
    country: str
    city: str
    address: str
    media_url: Optional[str] = None
    website_url: Optional[str] = None
    seat_count: int
    section_count: int


class VenueCreate(VenueBase):
    pass


class VenueUpdate(BaseModel):
    name: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    media_url: Optional[str] = None
    website_url: Optional[str] = None
    seat_count: Optional[int] = None
    section_count: Optional[int] = None


class VenueResponse(VenueBase):
    venue_id: int
    owner_id: int

    class Config:
        from_attributes = True
