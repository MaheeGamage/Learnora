from sqlalchemy import Column, String, JSON
from app.database.base import BaseModel


class LearningPath(BaseModel):
    """SQLAlchemy model for learning paths"""
    __tablename__ = "learning_path"

    thread_id = Column(String(50), unique=True, index=True, nullable=False)
    topic = Column(String(255), nullable=False)
    graph_state = Column(JSON, nullable=True)  # Store graph state
    status = Column(String(50), default="active")  # active, completed, paused

    def __repr__(self):
        return f"<LearningPath(thread_id={self.thread_id}, topic={self.topic})>"