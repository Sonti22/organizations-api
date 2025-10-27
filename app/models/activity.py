"""Activity model with Materialized Path for tree structure."""

import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import CheckConstraint, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.organization import Organization


class Activity(Base, UUIDMixin, TimestampMixin):
    """
    Activity model with tree structure (Materialized Path).
    
    Tree structure using 'path' field:
    - Level 1: '001'
    - Level 2: '001.002'
    - Level 3: '001.002.003'
    
    Max depth is limited to 3 levels.
    
    Attributes:
        id: UUID primary key
        name: Activity name (e.g., "Еда", "Мясная продукция")
        path: Materialized path (e.g., "001.002.003")
        level: Tree level (1, 2, or 3)
        parent_id: Parent activity UUID (nullable for root)
        parent: Parent activity relationship
        children: Child activities
        organizations: Related organizations
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    __tablename__ = "activities"

    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    
    # Materialized Path: '001', '001.002', '001.002.003'
    path: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
    )
    
    # Level: 1, 2, 3 (max depth = 3)
    level: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
    )
    
    # Self-referential FK to parent
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("activities.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    # Relationships
    parent: Mapped[Optional["Activity"]] = relationship(
        "Activity",
        remote_side="Activity.id",
        back_populates="children",
    )
    
    children: Mapped[list["Activity"]] = relationship(
        "Activity",
        back_populates="parent",
        cascade="all, delete-orphan",
    )
    
    organizations: Mapped[list["Organization"]] = relationship(
        "Organization",
        secondary="organization_activities",
        back_populates="activities",
    )

    __table_args__ = (
        CheckConstraint("level >= 1 AND level <= 3", name="check_activity_level"),
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<Activity(id={self.id}, name='{self.name}', level={self.level})>"


