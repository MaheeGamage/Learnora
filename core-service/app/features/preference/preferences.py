"""
User learning preferences and interaction tracking models.
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON, Float, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.database.base import Base


class LearningStyleEnum(enum.Enum):
    """Learning style preferences."""
    VISUAL = "visual"
    AUDITORY = "auditory"
    READING = "reading"
    KINESTHETIC = "kinesthetic"
    BALANCED = "balanced"


class InteractionTypeEnum(enum.Enum):
    """Types of content interactions."""
    VIEWED = "viewed"
    CLICKED = "clicked"
    COMPLETED = "completed"
    BOOKMARKED = "bookmarked"
    SHARED = "shared"
    RATED = "rated"


class UserLearningPreferences(Base):
    """
    Explicit user learning preferences.
    Users can set these manually, and they evolve based on interactions.
    """
    __tablename__ = "user_learning_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # Format preferences (JSON array: ["video", "article", "tutorial"])
    preferred_formats = Column(JSON, default=list, nullable=False)
    
    # Learning style
    learning_style = Column(
        Enum(LearningStyleEnum),
        default=LearningStyleEnum.BALANCED,
        nullable=False
    )
    
    # Time availability (minutes per day)
    available_time_daily = Column(Integer, default=60, nullable=False)
    
    # Knowledge areas (JSON dict: {"python": "intermediate", "react": "beginner"})
    knowledge_areas = Column(JSON, default=dict, nullable=False)
    
    # Learning goals (JSON array: ["master python", "learn web dev"])
    learning_goals = Column(JSON, default=list, nullable=False)
    
    # Difficulty preference
    preferred_difficulty = Column(String(50), default="intermediate", nullable=False)
    
    # Auto-evolve from interactions (if true, preferences adapt based on behavior)
    auto_evolve = Column(Integer, default=1, nullable=False)  # SQLite doesn't have native boolean
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="learning_preferences")
    
    def __repr__(self) -> str:
        return f"<UserLearningPreferences(user_id={self.user_id}, style={self.learning_style})>"


class ContentInteraction(Base):
    """
    Tracks user interactions with content for implicit preference learning.
    """
    __tablename__ = "content_interactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    
    # Content details
    content_id = Column(String(255), nullable=False, index=True)
    content_title = Column(String(500), nullable=True)
    content_type = Column(String(100), nullable=True)  # video, article, tutorial, etc.
    content_difficulty = Column(String(50), nullable=True)
    content_duration_minutes = Column(Integer, nullable=True)
    content_tags = Column(JSON, default=list, nullable=False)
    
    # Interaction details
    interaction_type = Column(
        Enum(InteractionTypeEnum),
        nullable=False,
        index=True
    )
    
    # Duration spent on content (seconds)
    duration_seconds = Column(Integer, default=0, nullable=False)
    
    # Rating (1-5 stars, optional)
    rating = Column(Float, nullable=True)
    
    # Completion percentage (0-100)
    completion_percentage = Column(Integer, default=0, nullable=False)
    
    # Timestamp
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="content_interactions")
    
    def __repr__(self) -> str:
        return f"<ContentInteraction(user_id={self.user_id}, content_id={self.content_id}, type={self.interaction_type})>"


# Add relationships to User model (will be imported in users/models.py)
