from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from app.features.learning_path.models import LearningPath
from app.features.learning_path.schemas import LearningPathCreate, LearningPathUpdate


async def create_learning_path(db: AsyncSession, learning_path: LearningPathCreate) -> LearningPath:
    """Create a new learning path in the database"""
    db_learning_path = LearningPath(**learning_path.model_dump())
    db.add(db_learning_path)
    await db.commit()
    await db.refresh(db_learning_path)
    return db_learning_path


async def get_learning_path_by_thread_id(db: AsyncSession, conversation_thread_id: str) -> Optional[LearningPath]:
    """Get learning path by conversation_thread_id"""
    result = await db.execute(
        select(LearningPath).where(LearningPath.conversation_thread_id == conversation_thread_id)
    )
    return result.scalar_one_or_none()


async def get_learning_path_by_id(db: AsyncSession, learning_path_id: int) -> Optional[LearningPath]:
    """Get learning path by ID"""
    result = await db.execute(
        select(LearningPath).where(LearningPath.id == learning_path_id)
    )
    return result.scalar_one_or_none()


async def get_all_learning_paths(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[LearningPath]:
    """Get all learning paths with pagination"""
    result = await db.execute(
        select(LearningPath).offset(skip).limit(limit)
    )
    return result.scalars().all()


async def update_learning_path(
    db: AsyncSession, 
    conversation_thread_id: str, 
    update_data: LearningPathUpdate
) -> Optional[LearningPath]:
    """Update learning path"""
    db_learning_path = await get_learning_path_by_thread_id(db, conversation_thread_id)
    if db_learning_path:
        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(db_learning_path, key, value)
        await db.commit()
        await db.refresh(db_learning_path)
    return db_learning_path


async def delete_learning_path(db: AsyncSession, conversation_thread_id: str) -> bool:
    """Delete a learning path"""
    db_learning_path = await get_learning_path_by_thread_id(db, conversation_thread_id)
    if db_learning_path:
        await db.delete(db_learning_path)
        await db.commit()
        return True
    return False