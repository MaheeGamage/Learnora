"""FastAPI router for content personalization endpoints."""

import logging
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.features.users.users import current_active_user
from app.features.users.models import User

from .service import ContentPersonalizationService
from .schemas import (
    PersonalizeRequest,
    PersonalizedContentSchema,
    SummarizeRequest,
    ContentSummarySchema,
    AdaptDifficultyRequest,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/content-personalization", tags=["content-personalization"])

# Global service instance
_personalization_service: ContentPersonalizationService | None = None


def get_personalization_service() -> ContentPersonalizationService:
    """Get or create the personalization service instance."""
    global _personalization_service
    if _personalization_service is None:
        _personalization_service = ContentPersonalizationService()
    return _personalization_service


@router.post("/personalize", response_model=PersonalizedContentSchema)
async def personalize_content(
    request: PersonalizeRequest,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
) -> PersonalizedContentSchema:
    """
    Personalize learning content for a specific user.
    
    - **content_id**: ID of the content to personalize
    - **user_level**: User's skill level (beginner, intermediate, advanced, expert)
    - **max_summary_words**: Maximum words for summary (50-500)
    - **user_time_budget**: Available time in minutes
    - **include_highlights**: Whether to extract video highlights
    
    Returns personalized content with:
    - Level-appropriate summary
    - TL;DR (very brief summary)
    - Video highlights (if applicable)
    - Adjusted time estimate
    - Key takeaways
    """
    service = get_personalization_service()
    
    # Get the content from discovery service
    from app.features.content_discovery.router import get_discovery_service
    discovery_service = get_discovery_service()
    
    content = discovery_service.vector_db.contents.get(request.content_id)
    if not content:
        raise HTTPException(status_code=404, detail=f"Content {request.content_id} not found")
    
    try:
        personalized = service.personalize_content(
            content=content,
            user_level=request.user_level,
            max_summary_words=request.max_summary_words,
            user_time_budget=request.user_time_budget,
            include_highlights=request.include_highlights,
        )
        
        return PersonalizedContentSchema(
            content_id=personalized.content_id,
            original_title=personalized.original_title,
            original_description=personalized.original_description,
            personalized_summary=personalized.personalized_summary,
            tldr=personalized.tldr,
            highlights=personalized.highlights,
            adapted_difficulty=personalized.adapted_difficulty,
            estimated_time=personalized.estimated_time,
            key_takeaways=personalized.key_takeaways,
            personalization_level=personalized.personalization_level,
            generated_at=personalized.generated_at,
        )
    except Exception as e:
        logger.error(f"Personalization failed: {e}")
        raise HTTPException(status_code=500, detail=f"Personalization failed: {str(e)}")


@router.post("/summarize", response_model=ContentSummarySchema)
async def summarize_content(
    request: SummarizeRequest,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ContentSummarySchema:
    """
    Generate a level-appropriate summary of content.
    
    - **content_id**: ID of the content to summarize
    - **user_level**: Target user level (beginner, intermediate, advanced, expert)
    - **max_words**: Maximum words for summary (50-500)
    
    Returns a summary adapted to the user's level with key points.
    """
    service = get_personalization_service()
    
    # Get the content
    from app.features.content_discovery.router import get_discovery_service
    discovery_service = get_discovery_service()
    
    content = discovery_service.vector_db.contents.get(request.content_id)
    if not content:
        raise HTTPException(status_code=404, detail=f"Content {request.content_id} not found")
    
    try:
        summary = service.generate_summary(
            content=content,
            user_level=request.user_level,
            max_words=request.max_words,
        )
        
        return ContentSummarySchema(
            original_length=summary.original_length,
            summary_length=summary.summary_length,
            summary_text=summary.summary_text,
            key_points=summary.key_points,
            difficulty_level=summary.difficulty_level,
            created_at=summary.created_at,
        )
    except Exception as e:
        logger.error(f"Summarization failed: {e}")
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")


@router.post("/adapt-difficulty")
async def adapt_difficulty(
    request: AdaptDifficultyRequest,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, str]:
    """
    Adapt content difficulty from one level to another.
    
    - **text**: Text content to adapt
    - **current_level**: Current difficulty level
    - **target_level**: Target difficulty level
    
    Returns the adapted text at the target level.
    """
    service = get_personalization_service()
    
    try:
        adapted_text = service.adapt_content_difficulty(
            text=request.text,
            current_level=request.current_level,
            target_level=request.target_level,
        )
        
        return {
            "original_level": request.current_level,
            "target_level": request.target_level,
            "adapted_text": adapted_text,
        }
    except Exception as e:
        logger.error(f"Difficulty adaptation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Adaptation failed: {str(e)}")


@router.get("/stats")
async def get_stats(
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Dict:
    """Get content personalization statistics."""
    service = get_personalization_service()
    
    return {
        "service_active": service is not None,
        "model_name": "gemini-2.0-flash-exp",
        "supported_levels": ["beginner", "intermediate", "advanced", "expert"],
        "features": [
            "content_summarization",
            "video_highlights",
            "difficulty_adaptation",
            "time_estimation",
        ],
    }
