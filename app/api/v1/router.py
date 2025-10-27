"""API v1 router."""

from fastapi import APIRouter

from app.api.v1.endpoints import activities, buildings, organizations

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(organizations.router)
api_router.include_router(buildings.router)
api_router.include_router(activities.router)

