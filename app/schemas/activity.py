"""Pydantic schemas for Activity."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class ActivityBase(BaseModel):
    """Base Activity schema."""

    name: str = Field(..., min_length=1, max_length=200, description="Activity name")


class ActivityCreate(ActivityBase):
    """Schema for creating an Activity."""

    parent_id: uuid.UUID | None = Field(None, description="Parent activity ID (null for root)")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate name is not empty after strip."""
        if not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()


class ActivityUpdate(BaseModel):
    """Schema for updating an Activity."""

    name: str | None = Field(None, min_length=1, max_length=200)


class ActivityInDB(ActivityBase):
    """Activity schema with DB fields."""

    id: uuid.UUID
    path: str
    level: int
    parent_id: uuid.UUID | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ActivityResponse(ActivityInDB):
    """Activity response schema."""

    pass


class ActivityTreeNode(BaseModel):
    """Activity tree node for hierarchical response."""

    id: uuid.UUID
    name: str
    path: str
    level: int
    parent_id: uuid.UUID | None
    children: list["ActivityTreeNode"] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class ActivityListResponse(BaseModel):
    """Paginated list of activities."""

    items: list[ActivityResponse]
    total: int
    page: int = 1
    size: int = 50

