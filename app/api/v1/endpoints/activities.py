"""Activity endpoints."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.security import verify_api_key
from app.models import Activity
from app.schemas import (
    ActivityCreate,
    ActivityListResponse,
    ActivityResponse,
    ActivityTreeNode,
    ActivityUpdate,
)

router = APIRouter(prefix="/activities", tags=["Activities"], dependencies=[Depends(verify_api_key)])


async def _generate_path(db: AsyncSession, parent_id: uuid.UUID | None) -> tuple[str, int]:
    """
    Generate materialized path for new activity.
    
    Returns:
        tuple: (path, level)
    """
    if parent_id is None:
        # Root level - find next available number
        query = select(Activity).where(Activity.level == 1).order_by(Activity.path.desc())
        result = await db.execute(query)
        last_root = result.scalars().first()
        
        if last_root:
            last_num = int(last_root.path)
            new_num = last_num + 1
        else:
            new_num = 1
        
        return f"{new_num:03d}", 1
    
    # Child level - get parent and append
    parent_query = select(Activity).where(Activity.id == parent_id)
    parent_result = await db.execute(parent_query)
    parent = parent_result.scalar_one_or_none()
    
    if not parent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Parent activity {parent_id} not found",
        )
    
    new_level = parent.level + 1
    
    if new_level > settings.max_activity_depth:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum activity depth is {settings.max_activity_depth}",
        )
    
    # Find next available child number
    children_query = (
        select(Activity)
        .where(Activity.parent_id == parent_id)
        .order_by(Activity.path.desc())
    )
    children_result = await db.execute(children_query)
    last_child = children_result.scalars().first()
    
    if last_child:
        last_num = int(last_child.path.split(".")[-1])
        new_num = last_num + 1
    else:
        new_num = 1
    
    new_path = f"{parent.path}.{new_num:03d}"
    return new_path, new_level


@router.get("", response_model=ActivityListResponse, summary="Get all activities")
async def get_activities(
    db: Annotated[AsyncSession, Depends(get_db)],
    level: int | None = Query(None, ge=1, le=3, description="Filter by level"),
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
) -> ActivityListResponse:
    """Get all activities with optional level filter."""
    query = select(Activity)
    
    if level is not None:
        query = query.where(Activity.level == level)
    
    # Count total
    count_query = select(func.count()).select_from(Activity)
    if level is not None:
        count_query = count_query.where(Activity.level == level)
    
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()
    
    # Order by path for tree order
    query = query.order_by(Activity.path).offset((page - 1) * size).limit(size)
    result = await db.execute(query)
    items = result.scalars().all()
    
    return ActivityListResponse(
        items=[ActivityResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        size=size,
    )


@router.get("/tree", response_model=list[ActivityTreeNode], summary="Get activity tree")
async def get_activity_tree(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[ActivityTreeNode]:
    """
    Get all activities as hierarchical tree structure.
    
    Returns tree with up to 3 levels.
    """
    query = select(Activity).order_by(Activity.path)
    result = await db.execute(query)
    all_activities = result.scalars().all()
    
    # Build tree
    tree_map: dict[uuid.UUID, ActivityTreeNode] = {}
    roots: list[ActivityTreeNode] = []
    
    for activity in all_activities:
        node = ActivityTreeNode(
            id=activity.id,
            name=activity.name,
            path=activity.path,
            level=activity.level,
            parent_id=activity.parent_id,
            children=[],
        )
        tree_map[activity.id] = node
        
        if activity.parent_id is None:
            roots.append(node)
        else:
            # Add to parent's children
            parent = tree_map.get(activity.parent_id)
            if parent:
                parent.children.append(node)
    
    return roots


@router.get("/{activity_id}", response_model=ActivityResponse, summary="Get activity by ID")
async def get_activity(
    activity_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ActivityResponse:
    """Get activity by UUID."""
    query = select(Activity).where(Activity.id == activity_id)
    result = await db.execute(query)
    activity = result.scalar_one_or_none()
    
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Activity {activity_id} not found",
        )
    
    return ActivityResponse.model_validate(activity)


@router.post("", response_model=ActivityResponse, status_code=status.HTTP_201_CREATED, summary="Create activity")
async def create_activity(
    data: ActivityCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ActivityResponse:
    """
    Create a new activity.
    
    - **name**: Activity name
    - **parent_id**: Parent activity UUID (null for root level)
    
    Maximum tree depth is 3 levels.
    """
    # Generate path and level
    path, level = await _generate_path(db, data.parent_id)
    
    activity = Activity(
        name=data.name,
        path=path,
        level=level,
        parent_id=data.parent_id,
    )
    
    db.add(activity)
    await db.commit()
    await db.refresh(activity)
    
    return ActivityResponse.model_validate(activity)


@router.put("/{activity_id}", response_model=ActivityResponse, summary="Update activity")
async def update_activity(
    activity_id: uuid.UUID,
    data: ActivityUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ActivityResponse:
    """
    Update activity by UUID.
    
    Note: Cannot change parent_id (would require path recalculation for entire subtree).
    """
    query = select(Activity).where(Activity.id == activity_id)
    result = await db.execute(query)
    activity = result.scalar_one_or_none()
    
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Activity {activity_id} not found",
        )
    
    # Update name only
    if data.name is not None:
        activity.name = data.name
    
    await db.commit()
    await db.refresh(activity)
    
    return ActivityResponse.model_validate(activity)


@router.delete("/{activity_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete activity")
async def delete_activity(
    activity_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Delete activity by UUID. Will cascade delete child activities."""
    query = select(Activity).where(Activity.id == activity_id)
    result = await db.execute(query)
    activity = result.scalar_one_or_none()
    
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Activity {activity_id} not found",
        )
    
    await db.delete(activity)
    await db.commit()

