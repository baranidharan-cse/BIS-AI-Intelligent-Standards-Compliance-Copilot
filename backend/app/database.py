"""
Async SQLAlchemy engine and session factory.

Uses aiosqlite for SQLite (dev) and can be swapped to asyncpg for Postgres
without changing any service code — only DATABASE_URL needs to change.
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings

settings = get_settings()

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    # SQLite-specific: allow use across threads in async context
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """Shared declarative base for all ORM models."""
    pass


async def get_db() -> AsyncSession:
    """FastAPI dependency: yields an async DB session per request."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_db() -> None:
    """Create all tables on startup (idempotent)."""
    # Import models to ensure they are registered on Base.metadata
    from app.models import (  # noqa: F401
        material,
        learning_path,
        quiz,
        revision,
        chat,
        progress,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
