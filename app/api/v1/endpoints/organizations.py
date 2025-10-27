"""Organization endpoints."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from geoalchemy2.functions import ST_DWithin, ST_GeogFromText, ST_MakeEnvelope

from app.core.database import get_db
from app.core.security import verify_api_key
from app.models import Activity, Building, Organization
from app.schemas import OrganizationCreate, OrganizationListResponse, OrganizationResponse, OrganizationUpdate

router = APIRouter(prefix="/organizations", tags=["Organizations"], dependencies=[Depends(verify_api_key)])


@router.get("", response_model=OrganizationListResponse, summary="Get all organizations")
async def get_organizations(
    db: Annotated[AsyncSession, Depends(get_db)],
    building_id: uuid.UUID | None = Query(None, description="Filter by building ID"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Page size"),
) -> OrganizationListResponse:
    """
    Get all organizations with optional filtering.
    
    - **building_id**: Filter organizations in specific building
    - **page**: Page number (1-based)
    - **size**: Items per page (max 100)
    """
    query = select(Organization).options(
        joinedload(Organization.building),
        joinedload(Organization.activities),
    )
    
    if building_id:
        query = query.where(Organization.building_id == building_id)
    
    # Count total
    count_query = select(func.count()).select_from(Organization)
    if building_id:
        count_query = count_query.where(Organization.building_id == building_id)
    
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()
    
    # Paginate
    query = query.offset((page - 1) * size).limit(size)
    result = await db.execute(query)
    items = result.scalars().unique().all()
    
    return OrganizationListResponse(
        items=[OrganizationResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        size=size,
    )


@router.get("/{organization_id}", response_model=OrganizationResponse, summary="Get organization by ID")
async def get_organization(
    organization_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> OrganizationResponse:
    """Get organization by UUID."""
    query = (
        select(Organization)
        .where(Organization.id == organization_id)
        .options(
            joinedload(Organization.building),
            joinedload(Organization.activities),
        )
    )
    
    result = await db.execute(query)
    organization = result.scalars().unique().first()
    
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organization {organization_id} not found",
        )
    
    return OrganizationResponse.model_validate(organization)


@router.post("", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED, summary="Create organization")
async def create_organization(
    data: OrganizationCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> OrganizationResponse:
    """
    Create a new organization.
    
    - **name**: Organization name
    - **phones**: List of phone numbers (at least 1)
    - **building_id**: Building UUID
    - **activity_ids**: List of activity UUIDs (at least 1)
    """
    # Verify building exists
    building_query = select(Building).where(Building.id == data.building_id)
    building_result = await db.execute(building_query)
    building = building_result.scalar_one_or_none()
    
    if not building:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Building {data.building_id} not found",
        )
    
    # Verify activities exist
    activities_query = select(Activity).where(Activity.id.in_(data.activity_ids))
    activities_result = await db.execute(activities_query)
    activities = activities_result.scalars().all()
    
    if len(activities) != len(data.activity_ids):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or more activities not found",
        )
    
    # Create organization
    organization = Organization(
        name=data.name,
        phones=data.phones,
        building_id=data.building_id,
        activities=list(activities),
    )
    
    db.add(organization)
    await db.commit()
    await db.refresh(organization)
    
    # Load relationships
    query = (
        select(Organization)
        .where(Organization.id == organization.id)
        .options(
            joinedload(Organization.building),
            joinedload(Organization.activities),
        )
    )
    result = await db.execute(query)
    organization = result.scalars().unique().first()
    
    return OrganizationResponse.model_validate(organization)


@router.put("/{organization_id}", response_model=OrganizationResponse, summary="Update organization")
async def update_organization(
    organization_id: uuid.UUID,
    data: OrganizationUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> OrganizationResponse:
    """Update organization by UUID."""
    query = select(Organization).where(Organization.id == organization_id)
    result = await db.execute(query)
    organization = result.scalar_one_or_none()
    
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organization {organization_id} not found",
        )
    
    # Update fields
    if data.name is not None:
        organization.name = data.name
    if data.phones is not None:
        organization.phones = data.phones
    if data.building_id is not None:
        # Verify building exists
        building_query = select(Building).where(Building.id == data.building_id)
        building_result = await db.execute(building_query)
        if not building_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Building {data.building_id} not found",
            )
        organization.building_id = data.building_id
    
    if data.activity_ids is not None:
        # Verify activities exist
        activities_query = select(Activity).where(Activity.id.in_(data.activity_ids))
        activities_result = await db.execute(activities_query)
        activities = activities_result.scalars().all()
        
        if len(activities) != len(data.activity_ids):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="One or more activities not found",
            )
        organization.activities = list(activities)
    
    await db.commit()
    await db.refresh(organization)
    
    # Load relationships
    query = (
        select(Organization)
        .where(Organization.id == organization.id)
        .options(
            joinedload(Organization.building),
            joinedload(Organization.activities),
        )
    )
    result = await db.execute(query)
    organization = result.scalars().unique().first()
    
    return OrganizationResponse.model_validate(organization)


@router.delete("/{organization_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete organization")
async def delete_organization(
    organization_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Delete organization by UUID."""
    query = select(Organization).where(Organization.id == organization_id)
    result = await db.execute(query)
    organization = result.scalar_one_or_none()
    
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organization {organization_id} not found",
        )
    
    await db.delete(organization)
    await db.commit()


@router.get("/by-activity/{activity_id}", response_model=OrganizationListResponse, summary="Get organizations by activity")
async def get_organizations_by_activity(
    activity_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    include_nested: bool = Query(True, description="Include nested activities (tree search)"),
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
) -> OrganizationListResponse:
    """
    Get organizations by activity ID.
    
    - **activity_id**: Activity UUID
    - **include_nested**: If True, includes organizations from nested activities (tree search)
    
    Example: Search for "Еда" (level 1) will also find organizations with "Мясная продукция" (level 2).
    """
    # Get activity
    activity_query = select(Activity).where(Activity.id == activity_id)
    activity_result = await db.execute(activity_query)
    activity = activity_result.scalar_one_or_none()
    
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Activity {activity_id} not found",
        )
    
    if include_nested:
        # Find all nested activities using path (e.g., path LIKE '001%')
        nested_query = select(Activity.id).where(Activity.path.like(f"{activity.path}%"))
        nested_result = await db.execute(nested_query)
        activity_ids = nested_result.scalars().all()
    else:
        activity_ids = [activity_id]
    
    # Find organizations
    query = (
        select(Organization)
        .join(Organization.activities)
        .where(Activity.id.in_(activity_ids))
        .options(
            joinedload(Organization.building),
            joinedload(Organization.activities),
        )
        .distinct()
    )
    
    # Count total
    count_query = (
        select(func.count(Organization.id.distinct()))
        .join(Organization.activities)
        .where(Activity.id.in_(activity_ids))
    )
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()
    
    # Paginate
    query = query.offset((page - 1) * size).limit(size)
    result = await db.execute(query)
    items = result.scalars().unique().all()
    
    return OrganizationListResponse(
        items=[OrganizationResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        size=size,
    )


@router.get("/search/name", response_model=OrganizationListResponse, summary="Search organizations by name")
async def search_organizations(
    db: Annotated[AsyncSession, Depends(get_db)],
    query_text: str = Query(..., alias="query", min_length=1, description="Search query"),
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
) -> OrganizationListResponse:
    """
    Search organizations by name (case-insensitive, partial match).
    
    - **query**: Search text (e.g., "Рога")
    """
    search_pattern = f"%{query_text.lower()}%"
    
    query = (
        select(Organization)
        .where(func.lower(Organization.name).like(search_pattern))
        .options(
            joinedload(Organization.building),
            joinedload(Organization.activities),
        )
    )
    
    # Count total
    count_query = (
        select(func.count())
        .select_from(Organization)
        .where(func.lower(Organization.name).like(search_pattern))
    )
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()
    
    # Paginate
    query = query.offset((page - 1) * size).limit(size)
    result = await db.execute(query)
    items = result.scalars().unique().all()
    
    return OrganizationListResponse(
        items=[OrganizationResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        size=size,
    )


@router.get("/geo/radius", response_model=OrganizationListResponse, summary="Find organizations within radius")
async def get_organizations_in_radius(
    db: Annotated[AsyncSession, Depends(get_db)],
    latitude: float = Query(..., ge=-90, le=90, description="Center latitude"),
    longitude: float = Query(..., ge=-180, le=180, description="Center longitude"),
    radius_meters: int = Query(..., ge=1, le=100000, description="Radius in meters (max 100km)"),
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
) -> OrganizationListResponse:
    """
    Find organizations within radius from point.
    
    Uses PostGIS ST_DWithin for efficient geographic search.
    
    - **latitude**: Center point latitude (WGS84)
    - **longitude**: Center point longitude (WGS84)
    - **radius_meters**: Search radius in meters (max 100km)
    """
    # Create point from lat/lon
    point_wkt = f"POINT({longitude} {latitude})"
    point_geog = ST_GeogFromText(point_wkt)
    
    # Query organizations within radius
    query = (
        select(Organization)
        .join(Organization.building)
        .where(ST_DWithin(Building.location, point_geog, radius_meters))
        .options(
            joinedload(Organization.building),
            joinedload(Organization.activities),
        )
    )
    
    # Count total
    count_query = (
        select(func.count())
        .select_from(Organization)
        .join(Organization.building)
        .where(ST_DWithin(Building.location, point_geog, radius_meters))
    )
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()
    
    # Paginate
    query = query.offset((page - 1) * size).limit(size)
    result = await db.execute(query)
    items = result.scalars().unique().all()
    
    return OrganizationListResponse(
        items=[OrganizationResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        size=size,
    )


@router.get("/geo/bbox", response_model=OrganizationListResponse, summary="Find organizations in bounding box")
async def get_organizations_in_bbox(
    db: Annotated[AsyncSession, Depends(get_db)],
    min_lat: float = Query(..., ge=-90, le=90, description="Minimum latitude"),
    max_lat: float = Query(..., ge=-90, le=90, description="Maximum latitude"),
    min_lon: float = Query(..., ge=-180, le=180, description="Minimum longitude"),
    max_lon: float = Query(..., ge=-180, le=180, description="Maximum longitude"),
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
) -> OrganizationListResponse:
    """
    Find organizations within bounding box (rectangular area).
    
    Uses PostGIS ST_MakeEnvelope for efficient geographic search.
    
    - **min_lat, max_lat**: Latitude range
    - **min_lon, max_lon**: Longitude range
    """
    # Validate bbox
    if min_lat >= max_lat:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="min_lat must be less than max_lat",
        )
    if min_lon >= max_lon:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="min_lon must be less than max_lon",
        )
    
    # Create envelope (bbox)
    envelope = ST_MakeEnvelope(min_lon, min_lat, max_lon, max_lat, 4326)
    
    # Query organizations in bbox
    query = (
        select(Organization)
        .join(Organization.building)
        .where(ST_DWithin(Building.location, envelope, 0))
        .options(
            joinedload(Organization.building),
            joinedload(Organization.activities),
        )
    )
    
    # Count total
    count_query = (
        select(func.count())
        .select_from(Organization)
        .join(Organization.building)
        .where(ST_DWithin(Building.location, envelope, 0))
    )
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()
    
    # Paginate
    query = query.offset((page - 1) * size).limit(size)
    result = await db.execute(query)
    items = result.scalars().unique().all()
    
    return OrganizationListResponse(
        items=[OrganizationResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        size=size,
    )

