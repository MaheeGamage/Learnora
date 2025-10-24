from sqlalchemy.orm import Session
from typing import Optional, List
from app.features.learning_path_planner.models import LearningPath
from app.features.learning_path_planner.schemas import LearningPathCreate, LearningPathUpdate


def create_learning_path(db: Session, learning_path: LearningPathCreate) -> LearningPath:
    """Create a new learning path in the database"""
    db_learning_path = LearningPath(**learning_path.model_dump())
    db.add(db_learning_path)
    db.commit()
    db.refresh(db_learning_path)
    return db_learning_path


def get_learning_path(db: Session, thread_id: str) -> Optional[LearningPath]:
    """Get learning path by thread_id"""
    return db.query(LearningPath).filter(
        LearningPath.thread_id == thread_id
    ).first()


def get_all_learning_paths(db: Session, skip: int = 0, limit: int = 100) -> List[LearningPath]:
    """Get all learning paths with pagination"""
    return db.query(LearningPath).offset(skip).limit(limit).all()


def update_learning_path(
    db: Session, 
    thread_id: str, 
    update_data: LearningPathUpdate
) -> Optional[LearningPath]:
    """Update learning path graph state or status"""
    db_learning_path = get_learning_path(db, thread_id)
    if db_learning_path:
        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(db_learning_path, key, value)
        db.commit()
        db.refresh(db_learning_path)
    return db_learning_path


def delete_learning_path(db: Session, thread_id: str) -> bool:
    """Delete a learning path"""
    db_learning_path = get_learning_path(db, thread_id)
    if db_learning_path:
        db.delete(db_learning_path)
        db.commit()
        return True
    return False