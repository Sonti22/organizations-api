"""Building model with PostGIS support."""

from typing import TYPE_CHECKING

from geoalchemy2 import Geography
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.organization import Organization


class Building(Base, UUIDMixin, TimestampMixin):
    """
    Building model with geographic location.
    
    Attributes:
        id: UUID primary key
        address: Full address (e.g., "г. Москва, ул. Ленина 1, офис 3")
        location: PostGIS GEOGRAPHY(POINT, 4326) - latitude/longitude
        organizations: Related organizations in this building
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    __tablename__ = "buildings"

    address: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    
    # PostGIS geography column (SRID=4326 for WGS84 lat/lon)
    location: Mapped[str] = mapped_column(
        Geography(geometry_type="POINT", srid=4326),
        nullable=False,
    )

    # Relationships
    organizations: Mapped[list["Organization"]] = relationship(
        "Organization",
        back_populates="building",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<Building(id={self.id}, address='{self.address}')>"


