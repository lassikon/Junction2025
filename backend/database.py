"""
Database configuration and session management for LifeSim.

This module handles:
- SQLite database connection
- Table creation
- Session management for async operations
"""

from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import os

# Database URL - uses SQLite by default
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./lifesim.db")

# For async operations, we need to use aiosqlite
if DATABASE_URL.startswith("sqlite"):
    ASYNC_DATABASE_URL = DATABASE_URL.replace(
        "sqlite:///", "sqlite+aiosqlite:///")
else:
    ASYNC_DATABASE_URL = DATABASE_URL

# Create sync engine for table creation
sync_engine = create_engine(
    DATABASE_URL,
    echo=True,  # Set to False in production
    connect_args={
        "check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Create async engine for async operations
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=True,  # Set to False in production
    future=True
)

# Create async session maker
async_session_maker = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


def create_db_and_tables():
    """
    Create all database tables.
    Call this on application startup.
    """
    SQLModel.metadata.create_all(sync_engine)
    print("✅ Database tables created successfully")


def get_sync_session():
    """
    Get a sync database session.
    Use this for simple operations or startup scripts.
    """
    with Session(sync_engine) as session:
        yield session


@asynccontextmanager
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get an async database session.
    Use this for all async FastAPI endpoints.

    Example usage in endpoint:
        async with get_async_session() as session:
            result = await session.execute(select(PlayerProfile))
            profiles = result.scalars().all()
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for FastAPI endpoints.

    Example usage:
        @app.get("/api/test")
        async def test_endpoint(session: AsyncSession = Depends(get_session)):
            result = await session.execute(select(PlayerProfile))
            return result.scalars().all()
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """
    Initialize database for async operations.
    Creates all tables using the async engine.
    """
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    print("✅ Async database initialized successfully")


async def close_db():
    """
    Close database connections.
    Call this on application shutdown.
    """
    await async_engine.dispose()
    print("✅ Database connections closed")
