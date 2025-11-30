"""Data models for content discovery."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class LearningContent:
    """Represents an item that can be recommended to a learner."""

    id: str
    title: str
    content_type: str
    source: str
    url: str
    description: str
    difficulty: str
    duration_minutes: int
    tags: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    checksum: Optional[str] = None

    def document_text(self) -> str:
        """Concatenate searchable fields into a single string."""
        parts: List[str] = [self.title, self.description]
        parts.extend(self.tags)
        parts.extend(self.prerequisites)
        for key, value in self.metadata.items():
            parts.append(f"{key}: {value}")
        return " ".join(part for part in parts if part)


@dataclass
class UserProfile:
    """Small representation of a learner used for personalization."""

    user_id: str
    knowledge_areas: Dict[str, str] = field(default_factory=dict)
    learning_goals: List[str] = field(default_factory=list)
    preferred_formats: List[str] = field(default_factory=list)
    available_time_daily: int = 60
    learning_style: str = "balanced"
