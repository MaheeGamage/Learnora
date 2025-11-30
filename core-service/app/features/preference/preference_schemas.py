"""
Pydantic schemas for learning preferences.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict


class PreferencesUpdate(BaseModel):
    """Schema for updating user preferences."""
    preferred_formats: Optional[List[str]] = Field(None, description="Preferred content formats")
    learning_style: Optional[str] = Field(None, description="Learning style preference")
    available_time_daily: Optional[int] = Field(None, ge=1, le=480, description="Available minutes per day")
    knowledge_areas: Optional[Dict[str, str]] = Field(None, description="Knowledge areas and proficiency")
    learning_goals: Optional[List[str]] = Field(None, description="Learning goals")
    preferred_difficulty: Optional[str] = Field(None, description="Preferred difficulty level")
    auto_evolve: Optional[bool] = Field(None, description="Auto-evolve from interactions")


class PreferencesResponse(BaseModel):
    """Schema for preferences response."""
    id: int
    user_id: int
    preferred_formats: List[str]
    learning_style: str
    available_time_daily: int
    knowledge_areas: Dict[str, str]
    learning_goals: List[str]
    preferred_difficulty: str
    auto_evolve: bool
    created_at: str
    updated_at: Optional[str]


class InteractionCreate(BaseModel):
    """Schema for creating a content interaction."""
    content_id: str = Field(..., description="Unique content identifier")
    interaction_type: str = Field(..., description="Type of interaction (viewed, clicked, completed, etc.)")
    content_title: Optional[str] = Field(None, description="Content title")
    content_type: Optional[str] = Field(None, description="Content type (video, article, etc.)")
    content_difficulty: Optional[str] = Field(None, description="Content difficulty level")
    content_duration_minutes: Optional[int] = Field(None, description="Content duration in minutes")
    content_tags: Optional[List[str]] = Field(None, description="Content tags/topics")
    duration_seconds: int = Field(0, ge=0, description="Time spent on content in seconds")
    rating: Optional[float] = Field(None, ge=1, le=5, description="User rating (1-5 stars)")
    completion_percentage: int = Field(0, ge=0, le=100, description="Completion percentage (0-100)")


class InteractionResponse(BaseModel):
    """Schema for interaction response."""
    id: int
    user_id: int
    content_id: str
    interaction_type: str
    content_title: Optional[str]
    content_type: Optional[str]
    content_difficulty: Optional[str]
    duration_seconds: int
    rating: Optional[float]
    completion_percentage: int
    timestamp: str


class InsightsResponse(BaseModel):
    """Schema for user learning insights."""
    preferences: Dict
    stats: Dict
    last_updated: Optional[str]
