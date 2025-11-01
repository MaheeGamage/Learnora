from sqlalchemy import ARRAY, Column, String
from app.database.base import BaseModel

class LearningPath(BaseModel):
    """SQLAlchemy model for learning paths"""
    __tablename__ = "learning_path"

    topic = Column(String(255), nullable=False)
    conversation_thread_id = Column(ARRAY(String(255)), index=True, nullable=False)
    graph_uri = Column(String(255), nullable=False, unique=True)

    def __repr__(self):
        return f"<LearningPath(id={self.id}, topic={self.topic}, conversation_thread_id={self.conversation_thread_id}, graph_uri={self.graph_uri})>"