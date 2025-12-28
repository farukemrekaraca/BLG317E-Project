from pydantic import BaseModel, field_validator
from typing import Optional, List


class SectionConfig(BaseModel):
    """Configuration for a section with prefix and seat count"""
    prefix: str
    seat_count: int

    @field_validator('seat_count')
    @classmethod
    def validate_seat_count(cls, v):
        if v <= 0:
            raise ValueError('Seat count must be positive')
        return v


class VenueBase(BaseModel):
    name: str
    country: str
    city: str
    address: str
    media_url: Optional[str] = None
    website_url: Optional[str] = None
    seat_count: int


class VenueCreate(VenueBase):
    sections: List[SectionConfig]

    @field_validator('sections')
    @classmethod
    def validate_sections(cls, v, info):
        if not v:
            raise ValueError('At least one section must be specified')

        # Check for duplicate prefixes
        prefixes = [s.prefix for s in v]
        if len(prefixes) != len(set(prefixes)):
            raise ValueError('Section prefixes must be unique')

        return v


class VenueUpdate(BaseModel):
    """Update venue metadata only - structure (sections/seats) cannot be changed after creation"""
    name: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    media_url: Optional[str] = None
    website_url: Optional[str] = None


class VenueResponse(VenueBase):
    venue_id: int
    owner_id: int
    section_count: int  # Derived from actual sections in DB

    class Config:
        from_attributes = True
