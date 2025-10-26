"""
Async database engine and session configuration.
Handles async connection to the database.
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from app.config import settings
import logging

logger = logging.getLogger(__name__)


def get_async_database_url(url: str) -> str:
    """Convert sync database URL to async"""
    if url.startswith("sqlite:///"):
        # SQLite: sqlite:///./test.db -> sqlite+aiosqlite:///./test.db
        return url.replace("sqlite:///", "sqlite+aiosqlite:///")
    elif url.startswith("postgresql://"):
        # PostgreSQL: postgresql://... -> postgresql+asyncpg://...
        return url.replace("postgresql://", "postgresql+asyncpg://")
    elif url.startswith("mysql://"):
        # MySQL: mysql://... -> mysql+aiomysql://...
        return url.replace("mysql://", "mysql+aiomysql://")
    return url


ASYNC_DATABASE_URL = get_async_database_url(settings.DATABASE_URL)

# Create ASYNC engine
engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
    # SQLite specific: disable pooling for file-based DBs
    poolclass=NullPool if ASYNC_DATABASE_URL.startswith("sqlite") else None,
)

# Create ASYNC session factory
SessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def init_db():
    """
    Initialize database tables asynchronously.
    Call this on application startup.
    """
    from app.database.base import Base
    
    logger.info("Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created successfully")


async def drop_db():
    """
    Drop all database tables asynchronously.
    USE WITH CAUTION - Only for development!
    """
    from app.database.base import Base
    
    if settings.APP_ENV == "production":
        raise RuntimeError("Cannot drop database in production!")
    
    logger.warning("Dropping all database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    logger.warning("All database tables dropped")