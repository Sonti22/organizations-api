"""Integration tests for API endpoints."""

import pytest
from httpx import AsyncClient
from geoalchemy2.shape import from_shape
from shapely.geometry import Point
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Activity, Building, Organization


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test health check endpoint."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient):
    """Test root endpoint."""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "app" in data
    assert "version" in data


@pytest.mark.asyncio
async def test_create_building(client: AsyncClient, api_headers: dict):
    """Test building creation."""
    payload = {
        "address": "г. Москва, ул. Тестовая, 1",
        "latitude": 55.7558,
        "longitude": 37.6173,
    }
    
    response = await client.post("/api/v1/buildings", json=payload, headers=api_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["address"] == payload["address"]
    assert data["latitude"] == payload["latitude"]
    assert data["longitude"] == payload["longitude"]


@pytest.mark.asyncio
async def test_create_activity(client: AsyncClient, api_headers: dict):
    """Test activity creation."""
    payload = {
        "name": "Тестовая деятельность",
        "parent_id": None,
    }
    
    response = await client.post("/api/v1/activities", json=payload, headers=api_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["level"] == 1
    assert data["path"] == "001"


@pytest.mark.asyncio
async def test_create_organization(client: AsyncClient, db_session: AsyncSession, api_headers: dict):
    """Test organization creation."""
    # Create building
    point = Point(37.6173, 55.7558)
    building = Building(
        address="г. Москва, ул. Тестовая, 1",
        location=from_shape(point, srid=4326),
    )
    db_session.add(building)
    
    # Create activity
    activity = Activity(
        name="Тест",
        path="001",
        level=1,
        parent_id=None,
    )
    db_session.add(activity)
    await db_session.commit()
    
    # Create organization
    payload = {
        "name": "ООО Тест",
        "phones": ["+7-123-456-78-90"],
        "building_id": str(building.id),
        "activity_ids": [str(activity.id)],
    }
    
    response = await client.post("/api/v1/organizations", json=payload, headers=api_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload["name"]
    assert len(data["phones"]) == 1


@pytest.mark.asyncio
async def test_get_organizations(client: AsyncClient, api_headers: dict):
    """Test get organizations list."""
    response = await client.get("/api/v1/organizations", headers=api_headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_unauthorized_request(client: AsyncClient):
    """Test request without API key."""
    response = await client.get("/api/v1/organizations")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_activity_tree(client: AsyncClient, api_headers: dict):
    """Test activity tree endpoint."""
    # Create activities
    response = await client.post(
        "/api/v1/activities",
        json={"name": "Parent", "parent_id": None},
        headers=api_headers,
    )
    assert response.status_code == 201
    parent_id = response.json()["id"]
    
    response = await client.post(
        "/api/v1/activities",
        json={"name": "Child", "parent_id": parent_id},
        headers=api_headers,
    )
    assert response.status_code == 201
    
    # Get tree
    response = await client.get("/api/v1/activities/tree", headers=api_headers)
    assert response.status_code == 200
    tree = response.json()
    assert len(tree) > 0
    assert tree[0]["children"]

