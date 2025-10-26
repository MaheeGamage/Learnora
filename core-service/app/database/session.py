"""
Async database session management and dependencies.
Provides async session lifecycle management for FastAPI routes.
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.connection import SessionLocal
import logging

logger = logging.getLogger(__name__)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Async database session dependency for FastAPI routes.
    
    Provides:
    - Automatic async session creation
    - Automatic session cleanup
    - Exception handling
    - Transaction management
    
    Usage in FastAPI routes:
    ```python
    @router.get("/items")
    async def get_items(db: AsyncSession = Depends(get_db)):
        result = await db.execute(select(Item))
        return result.scalars().all()
    ```
    
    The session is automatically:
    - Created before the route handler runs
    - Passed to the route handler
    - Closed after the route handler completes (even if error occurs)
    """
    async with SessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            logger.error(f"Database error occurred: {str(e)}")
            await session.rollback()
            raise
        finally:
            await session.close()