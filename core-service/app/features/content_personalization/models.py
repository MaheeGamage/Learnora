"""Data models for content personalization."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class VideoHighlight:
    """Represents a key moment in a video."""
    
    timestamp: str  # Format: "MM:SS" or "HH:MM:SS"
    topic: str
    description: str
    importance_score: float = 0.0  # 0.0 to 1.0


@dataclass
class ContentSummary:
    """Represents a summarized version of content."""
    
    original_length: int  # in words or minutes
    summary_length: int
    summary_text: str
    key_points: List[str] = field(default_factory=list)
    difficulty_level: str = "intermediate"
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PersonalizedContent:
    """Enhanced learning content with personalization."""
    
    content_id: str
    original_title: str
    original_description: str
    
    # Personalized fields
    personalized_summary: Optional[str] = None
    tldr: Optional[str] = None  # Very short summary (1-2 sentences)
    highlights: List[VideoHighlight] = field(default_factory=list)
    adapted_difficulty: Optional[str] = None
    estimated_time: Optional[int] = None  # in minutes, adjusted for user
    key_takeaways: List[str] = field(default_factory=list)
    
    # Metadata
    personalization_level: str = "basic"  # basic, standard, advanced
    generated_at: datetime = field(default_factory=datetime.utcnow)
