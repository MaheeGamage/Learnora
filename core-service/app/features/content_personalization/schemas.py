"""Pydantic schemas for content personalization API."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class VideoHighlightSchema(BaseModel):
    """Schema for video highlight."""
    
    timestamp: str = Field(..., description="Timestamp in MM:SS or HH:MM:SS format")
    topic: str = Field(..., description="Brief topic name")
    description: str = Field(..., description="What happens at this moment")
    importance_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Importance score 0-1")


class ContentSummarySchema(BaseModel):
    """Schema for content summary."""
    
    original_length: int = Field(..., description="Original content length in words/minutes")
    summary_length: int = Field(..., description="Summary length in words")
    summary_text: str = Field(..., description="The summarized text")
    key_points: List[str] = Field(default_factory=list, description="Key takeaways")
    difficulty_level: str = Field(default="intermediate", description="Target difficulty level")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class PersonalizedContentSchema(BaseModel):
    """Schema for personalized learning content."""
    
    content_id: str
    original_title: str
    original_description: str
    
    # Personalized fields
    personalized_summary: Optional[str] = None
    tldr: Optional[str] = None
    highlights: List[VideoHighlightSchema] = Field(default_factory=list)
    adapted_difficulty: Optional[str] = None
    estimated_time: Optional[int] = None
    key_takeaways: List[str] = Field(default_factory=list)
    
    # Metadata
    personalization_level: str = "basic"
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class PersonalizeRequest(BaseModel):
    """Request schema for content personalization."""
    
    content_id: str = Field(..., description="ID of content to personalize")
    user_level: str = Field(
        default="intermediate",
        description="User's skill level (beginner, intermediate, advanced, expert)"
    )
    max_summary_words: int = Field(
        default=200,
        ge=50,
        le=500,
        description="Maximum words for summary"
    )
    user_time_budget: Optional[int] = Field(
        default=None,
        description="User's available time in minutes"
    )
    include_highlights: bool = Field(
        default=True,
        description="Extract video highlights"
    )


class SummarizeRequest(BaseModel):
    """Request schema for content summarization."""
    
    content_id: str = Field(..., description="ID of content to summarize")
    user_level: str = Field(
        default="intermediate",
        description="Target user level"
    )
    max_words: int = Field(
        default=200,
        ge=50,
        le=500,
        description="Maximum words for summary"
    )


class AdaptDifficultyRequest(BaseModel):
    """Request schema for difficulty adaptation."""
    
    text: str = Field(..., description="Text content to adapt")
    current_level: str = Field(..., description="Current difficulty level")
    target_level: str = Field(..., description="Target difficulty level")
