"""API Key authentication middleware."""

from typing import Optional

from fastapi import Header, HTTPException, status

from app.core.config import settings


async def verify_api_key(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
) -> None:
    """Verify API Key from request header.

    Args:
        x_api_key: API key from X-API-Key header. May be ``None`` if the header is absent.

    Raises:
        HTTPException: 401 if API key is missing or invalid.

    Example:
        ```python
        @app.get("/organizations", dependencies=[Depends(verify_api_key)])
        async def get_organizations():
            ...
        ```
    """
    if not x_api_key or x_api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
