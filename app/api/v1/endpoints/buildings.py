"""Building endpoints."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from geoalchemy2.shape import from_shape, to_shape
from shapely.geometry import Point
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import verify_api_key
from app.models import Building
from app.schemas import BuildingCreate, BuildingListResponse, BuildingResponse, BuildingUpdate

router = APIRouter(prefix="/buildings", tags=["Buildings"], dependencies=[Depends(verify_api_key)])


@router.get("", response_model=BuildingListResponse, summary="Get all buildings")
async def get_buildings(
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
) -> BuildingListResponse:
    """Get all buildings with pagination."""
    query = select(Building)
    
    # Count total
    count_query = select(func.count()).select_from(Building)
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()
    
    # Paginate
    query = query.offset((page - 1) * size).limit(size)
    result = await db.execute(query)
    buildings = result.scalars().all()
    
    # Convert to response (extract lat/lon from PostGIS)
    items = []
    for building in buildings:
        point = to_shape(building.location)
        items.append(
            BuildingResponse(
                id=building.id,
                address=building.address,
                latitude=point.y,
                longitude=point.x,
                created_at=building.created_at,
                updated_at=building.updated_at,
            )
        )
    
    return BuildingListResponse(
        items=items,
        total=total,
        page=page,
        size=size,
    )


@router.get("/{building_id}", response_model=BuildingResponse, summary="Get building by ID")
async def get_building(
    building_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> BuildingResponse:
    """Get building by UUID."""
    query = select(Building).where(Building.id == building_id)
    result = await db.execute(query)
    building = result.scalar_one_or_none()
    
    if not building:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Building {building_id} not found",
        )
    
    point = to_shape(building.location)
    return BuildingResponse(
        id=building.id,
        address=building.address,
        latitude=point.y,
        longitude=point.x,
        created_at=building.created_at,
        updated_at=building.updated_at,
    )


@router.post("", response_model=BuildingResponse, status_code=status.HTTP_201_CREATED, summary="Create building")
async def create_building(
    data: BuildingCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> BuildingResponse:
    """
    Create a new building.
    
    - **address**: Full address
    - **latitude**: Latitude (WGS84, -90 to 90)
    - **longitude**: Longitude (WGS84, -180 to 180)
    """
    # Create PostGIS point
    point = Point(data.longitude, data.latitude)
    location_wkb = from_shape(point, srid=4326)
    
    building = Building(
        address=data.address,
        location=location_wkb,
    )
    
    db.add(building)
    await db.commit()
    await db.refresh(building)
    
    return BuildingResponse(
        id=building.id,
        address=building.address,
        latitude=data.latitude,
        longitude=data.longitude,
        created_at=building.created_at,
        updated_at=building.updated_at,
    )


@router.put("/{building_id}", response_model=BuildingResponse, summary="Update building")
async def update_building(
    building_id: uuid.UUID,
    data: BuildingUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> BuildingResponse:
    """Update building by UUID."""
    query = select(Building).where(Building.id == building_id)
    result = await db.execute(query)
    building = result.scalar_one_or_none()
    
    if not building:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Building {building_id} not found",
        )
    
    # Update fields
    if data.address is not None:
        building.address = data.address
    
    if data.latitude is not None or data.longitude is not None:
        # Get current location
        current_point = to_shape(building.location)
        new_lat = data.latitude if data.latitude is not None else current_point.y
        new_lon = data.longitude if data.longitude is not None else current_point.x
        
        new_point = Point(new_lon, new_lat)
        building.location = from_shape(new_point, srid=4326)
    
    await db.commit()
    await db.refresh(building)
    
    point = to_shape(building.location)
    return BuildingResponse(
        id=building.id,
        address=building.address,
        latitude=point.y,
        longitude=point.x,
        created_at=building.created_at,
        updated_at=building.updated_at,
    )


@router.delete("/{building_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete building")
async def delete_building(
    building_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Delete building by UUID. Will cascade delete related organizations."""
    query = select(Building).where(Building.id == building_id)
    result = await db.execute(query)
    building = result.scalar_one_or_none()
    
    if not building:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Building {building_id} not found",
        )
    
    await db.delete(building)
    await db.commit()

