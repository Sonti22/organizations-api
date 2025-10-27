"""Pydantic schemas for Building."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class BuildingBase(BaseModel):
    """Base Building schema."""

    address: str = Field(..., min_length=1, max_length=500, description="Full address")
    latitude: float = Field(..., ge=-90, le=90, description="Latitude (WGS84)")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude (WGS84)")


class BuildingCreate(BuildingBase):
    """Schema for creating a Building."""

    pass


class BuildingUpdate(BaseModel):
    """Schema for updating a Building."""

    address: str | None = Field(None, min_length=1, max_length=500)
    latitude: float | None = Field(None, ge=-90, le=90)
    longitude: float | None = Field(None, ge=-180, le=180)


class BuildingInDB(BuildingBase):
    """Building schema with DB fields."""

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class BuildingResponse(BuildingInDB):
    """Building response schema."""

    pass


class BuildingListResponse(BaseModel):
    """Paginated list of buildings."""

    items: list[BuildingResponse]
    total: int
    page: int = 1
    size: int = 50

