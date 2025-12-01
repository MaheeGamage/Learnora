"""
API routes for user learning preferences.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.features.users.models import User
from app.features.users.users import current_active_user
from .preference_service import PreferenceService
from .preference_schemas import (
    PreferencesUpdate,
    PreferencesResponse,
    InteractionCreate,
    InteractionResponse,
    InsightsResponse
)

router = APIRouter(prefix="/preferences", tags=["preferences"])


@router.get("/", response_model=PreferencesResponse)
async def get_preferences(
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's learning preferences."""
    service = PreferenceService(db)
    prefs = await service.get_or_create_preferences(user.id)
    
    return PreferencesResponse(
        id=prefs.id,
        user_id=prefs.user_id,
        preferred_formats=prefs.preferred_formats or [],
        learning_style=prefs.learning_style.value if prefs.learning_style else "balanced",
        available_time_daily=prefs.available_time_daily or 60,
        knowledge_areas=prefs.knowledge_areas or {},
        learning_goals=prefs.learning_goals or [],
        preferred_difficulty=prefs.preferred_difficulty or "intermediate",
        auto_evolve=bool(prefs.auto_evolve),
        created_at=prefs.created_at.isoformat(),
        updated_at=prefs.updated_at.isoformat() if prefs.updated_at else None
    )


@router.put("/", response_model=PreferencesResponse)
async def update_preferences(
    updates: PreferencesUpdate,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update user's learning preferences.
    
    - **preferred_formats**: Array of preferred content types (e.g., ["video", "article"])
    - **learning_style**: visual, auditory, reading, kinesthetic, or balanced
    - **available_time_daily**: Minutes available per day (1-480)
    - **knowledge_areas**: Dict of topics and proficiency (e.g., {"python": "intermediate"})
    - **learning_goals**: Array of learning goals
    - **preferred_difficulty**: beginner, intermediate, advanced, or expert
    - **auto_evolve**: Whether to auto-update preferences from interactions
    """
    service = PreferenceService(db)
    
    try:
        prefs = await service.update_preferences(
            user_id=user.id,
            preferred_formats=updates.preferred_formats,
            learning_style=updates.learning_style,
            available_time_daily=updates.available_time_daily,
            knowledge_areas=updates.knowledge_areas,
            learning_goals=updates.learning_goals,
            preferred_difficulty=updates.preferred_difficulty,
            auto_evolve=updates.auto_evolve
        )
        
        return PreferencesResponse(
            id=prefs.id,
            user_id=prefs.user_id,
            preferred_formats=prefs.preferred_formats or [],
            learning_style=prefs.learning_style.value if prefs.learning_style else "balanced",
            available_time_daily=prefs.available_time_daily or 60,
            knowledge_areas=prefs.knowledge_areas or {},
            learning_goals=prefs.learning_goals or [],
            preferred_difficulty=prefs.preferred_difficulty or "intermediate",
            auto_evolve=bool(prefs.auto_evolve),
            created_at=prefs.created_at.isoformat(),
            updated_at=prefs.updated_at.isoformat() if prefs.updated_at else None
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/interactions", response_model=InteractionResponse)
async def track_interaction(
    interaction: InteractionCreate,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Track a content interaction (view, click, completion, etc.).
    This data is used to evolve user preferences automatically.
    
    - **content_id**: Unique identifier for the content
    - **interaction_type**: viewed, clicked, completed, bookmarked, shared, or rated
    - **duration_seconds**: Time spent on content
    - **completion_percentage**: How much of the content was consumed (0-100)
    - **rating**: Optional rating (1-5 stars)
    """
    service = PreferenceService(db)
    
    try:
        tracked = await service.track_interaction(
            user_id=user.id,
            content_id=interaction.content_id,
            interaction_type=interaction.interaction_type,
            content_title=interaction.content_title,
            content_type=interaction.content_type,
            content_difficulty=interaction.content_difficulty,
            content_duration_minutes=interaction.content_duration_minutes,
            content_tags=interaction.content_tags,
            duration_seconds=interaction.duration_seconds,
            rating=interaction.rating,
            completion_percentage=interaction.completion_percentage
        )
        
        return InteractionResponse(
            id=tracked.id,
            user_id=tracked.user_id,
            content_id=tracked.content_id,
            interaction_type=tracked.interaction_type.value,
            content_title=tracked.content_title,
            content_type=tracked.content_type,
            content_difficulty=tracked.content_difficulty,
            duration_seconds=tracked.duration_seconds,
            rating=tracked.rating,
            completion_percentage=tracked.completion_percentage,
            timestamp=tracked.timestamp.isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/insights", response_model=InsightsResponse)
async def get_insights(
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get insights about user's learning patterns.
    
    Returns statistics about:
    - Current preferences (formats, style, difficulty, etc.)
    - Learning statistics (completions, ratings, streak)
    - How preferences have evolved over time
    """
    service = PreferenceService(db)
    insights = await service.get_insights(user.id)
    
    return InsightsResponse(**insights)
