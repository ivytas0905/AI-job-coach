"""Database Manager - SQLAlchemy async database connection and session management"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator
import logging

# Base class for all SQLAlchemy models
Base = declarative_base()

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Database Manager for handling SQLAlchemy async connections.

    Supports SQLite (development) and PostgreSQL (production).
    """

    def __init__(self, database_url: str, echo: bool = False):
        """
        Initialize database manager.

        Args:
            database_url: Database connection string
                - SQLite: "sqlite+aiosqlite:///./ai_job_coach.db"
                - PostgreSQL: "postgresql+asyncpg://user:pass@localhost:5432/db"
            echo: Whether to log SQL queries
        """
        self.database_url = database_url
        self.echo = echo

        # Create async engine
        self.engine = create_async_engine(
            database_url,
            echo=echo,
            future=True
        )

        # Create session factory
        self.async_session_factory = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

        logger.info(f"Database manager initialized with URL: {self._safe_url(database_url)}")

    def _safe_url(self, url: str) -> str:
        """Hide password in database URL for logging."""
        if '@' in url:
            # Hide password
            parts = url.split('@')
            if ':' in parts[0]:
                protocol_and_user = parts[0].rsplit(':', 1)[0]
                return f"{protocol_and_user}:****@{parts[1]}"
        return url

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Get async database session.

        Usage:
            async with db_manager.get_session() as session:
                # Use session
                pass

        Yields:
            AsyncSession: Database session
        """
        async with self.async_session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    async def create_tables(self):
        """
        Create all tables defined in models.

        This should be called during application startup.
        """
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")

    async def drop_tables(self):
        """
        Drop all tables.

        WARNING: This will delete all data! Use only in development/testing.
        """
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        logger.warning("All database tables dropped")

    async def close(self):
        """Close database engine and connections."""
        await self.engine.dispose()
        logger.info("Database connections closed")


# Helper function for dependency injection
_db_manager_instance = None


def get_db_manager(database_url: str = None, echo: bool = False) -> DatabaseManager:
    """
    Get singleton database manager instance.

    Args:
        database_url: Database URL (required on first call)
        echo: Whether to echo SQL queries

    Returns:
        DatabaseManager instance
    """
    global _db_manager_instance

    if _db_manager_instance is None:
        if database_url is None:
            raise ValueError("database_url is required for first initialization")
        _db_manager_instance = DatabaseManager(database_url, echo)

    return _db_manager_instance


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for FastAPI routes to get database session.

    Usage in route:
        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db_session)):
            # Use db session
            pass
    """
    db_manager = get_db_manager()
    async for session in db_manager.get_session():
        yield session
