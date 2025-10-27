"""API Key authentication middleware."""

from fastapi import Header, HTTPException, status

from app.core.config import settings


async def verify_api_key(x_api_key: str = Header(..., alias="X-API-Key")) -> None:
    """
    Verify API Key from request header.
    
    Args:
        x_api_key: API key from X-API-Key header
        
    Raises:
        HTTPException: 401 if API key is invalid
        
    Example:
        @app.get("/organizations", dependencies=[Depends(verify_api_key)])
        async def get_organizations():
            ...
    """
    if x_api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
            headers={"WWW-Authenticate": "ApiKey"},
        )


