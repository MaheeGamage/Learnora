from sqlalchemy import Column, Integer, String, ForeignKey
from app.database.base import BaseModel
from sqlalchemy.orm import relationship

class LearningPath(BaseModel):
    """SQLAlchemy model for learning paths"""
    __tablename__ = "learning_path"

    topic = Column(String(255), nullable=False)
    graph_uri = Column(String(255), nullable=True, unique=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    user = relationship("User")

    def __repr__(self):
        return f"<LearningPath(id={self.id}, topic={self.topic}, graph_uri={self.graph_uri}, user_id={self.user_id})>"