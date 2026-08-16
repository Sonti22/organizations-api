"""Database engine and session factory."""

from collections.abc import AsyncGenerator
from typing import NoReturn

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import settings

# Create async engine
engine = create_async_engine(
    settings.database_url_str,
    echo=settings.database_echo,
    poolclass=NullPool,  # Для dev, в prod использовать pool
    future=True,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for obtaining an async database session.

    Yields:
        AsyncSession: Database session instance

    Example:
        @app.get("/organizations")
        async def get_orgs(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
    # The async context manager automatically closes the session; no explicit close needed.
