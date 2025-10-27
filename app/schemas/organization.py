"""Pydantic schemas for Organization."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.schemas.activity import ActivityResponse
from app.schemas.building import BuildingResponse


class OrganizationBase(BaseModel):
    """Base Organization schema."""

    name: str = Field(..., min_length=1, max_length=500, description="Organization name")
    phones: list[str] = Field(..., min_items=1, description="List of phone numbers")

    @field_validator("phones")
    @classmethod
    def validate_phones(cls, v: list[str]) -> list[str]:
        """Validate phone numbers."""
        if not v:
            raise ValueError("At least one phone number is required")
        # Strip whitespace
        cleaned = [phone.strip() for phone in v if phone.strip()]
        if not cleaned:
            raise ValueError("Phone numbers cannot be empty")
        return cleaned


class OrganizationCreate(OrganizationBase):
    """Schema for creating an Organization."""

    building_id: uuid.UUID = Field(..., description="Building UUID where organization is located")
    activity_ids: list[uuid.UUID] = Field(
        ...,
        min_items=1,
        description="List of activity UUIDs",
    )


class OrganizationUpdate(BaseModel):
    """Schema for updating an Organization."""

    name: str | None = Field(None, min_length=1, max_length=500)
    phones: list[str] | None = Field(None, min_items=1)
    building_id: uuid.UUID | None = None
    activity_ids: list[uuid.UUID] | None = Field(None, min_items=1)

    @field_validator("phones")
    @classmethod
    def validate_phones(cls, v: list[str] | None) -> list[str] | None:
        """Validate phone numbers."""
        if v is None:
            return None
        if not v:
            raise ValueError("At least one phone number is required")
        cleaned = [phone.strip() for phone in v if phone.strip()]
        if not cleaned:
            raise ValueError("Phone numbers cannot be empty")
        return cleaned


class OrganizationInDB(OrganizationBase):
    """Organization schema with DB fields."""

    id: uuid.UUID
    building_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class OrganizationResponse(OrganizationInDB):
    """Organization response schema with related data."""

    building: BuildingResponse
    activities: list[ActivityResponse]

    model_config = {"from_attributes": True}


class OrganizationListResponse(BaseModel):
    """Paginated list of organizations."""

    items: list[OrganizationResponse]
    total: int
    page: int = 1
    size: int = 50

