"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan events."""
    # Startup
    print(f"🚀 Starting {settings.app_name} v{settings.app_version}")
    print(f"📊 API Docs: http://{settings.host}:{settings.port}/docs")
    yield
    # Shutdown
    print(f"🛑 Shutting down {settings.app_name}")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
REST API приложение для справочника **Организаций**, **Зданий** и **Деятельностей**.

## Возможности

- 🏢 **Организации** с привязкой к зданиям и видам деятельности
- 🏗️ **Здания** с географическими координатами (PostGIS)
- 🌳 **Древовидная структура** деятельностей (до 3 уровней)
- 🔍 **Геопространственный поиск** (радиус, bounding box)
- 🔐 **API Key** аутентификация

## Аутентификация

Все запросы требуют заголовок `X-API-Key`.

Пример:
```bash
curl -H "X-API-Key: your-api-key" http://localhost:8000/api/v1/organizations
```
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Include API router
app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/health", tags=["Health"], summary="Health check")
async def health_check() -> dict[str, str]:
    """
    Health check endpoint.
    
    Returns:
        dict: Status message
    """
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.app_version,
    }


@app.get("/", tags=["Root"], summary="Root endpoint")
async def root() -> dict[str, str]:
    """
    Root endpoint with API information.
    
    Returns:
        dict: API info
    """
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
    }


# Exception handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": "Resource not found"},
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle 500 errors."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )

