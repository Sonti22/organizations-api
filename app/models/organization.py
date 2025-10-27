"""Organization model with many-to-many relationships."""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ARRAY, ForeignKey, String, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.activity import Activity
    from app.models.building import Building


# Many-to-Many association table
organization_activities = Table(
    "organization_activities",
    Base.metadata,
    mapped_column("organization_id", UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), primary_key=True),
    mapped_column("activity_id", UUID(as_uuid=True), ForeignKey("activities.id", ondelete="CASCADE"), primary_key=True),
)


class Organization(Base, UUIDMixin, TimestampMixin):
    """
    Organization model.
    
    Attributes:
        id: UUID primary key
        name: Organization name (e.g., 'ООО "Рога и Копыта"')
        phones: Array of phone numbers
        building_id: Foreign key to building
        building: Related building
        activities: Related activities (many-to-many)
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    
    # Array of phone numbers
    phones: Mapped[list[str]] = mapped_column(
        ARRAY(String(50)),
        nullable=False,
        default=list,
    )
    
    # Foreign key to building
    building_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("buildings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Relationships
    building: Mapped["Building"] = relationship(
        "Building",
        back_populates="organizations",
    )
    
    activities: Mapped[list["Activity"]] = relationship(
        "Activity",
        secondary=organization_activities,
        back_populates="organizations",
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<Organization(id={self.id}, name='{self.name}')>"


