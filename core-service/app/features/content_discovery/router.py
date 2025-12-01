"""FastAPI router for content discovery endpoints."""

from typing import Dict, List
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.features.users.users import current_active_user
from app.features.users.models import User
from app.features.preference.preference_service import PreferenceService
from app.features.content_personalization.router import get_personalization_service

from .models import LearningContent, UserProfile
from .schemas import (
    CrawlRequest,
    CrawlResponse,
    IndexContentRequest,
    IndexContentResponse,
    LearningContentSchema,
    SearchRequest,
    SearchResponse,
    SetKeywordsRequest,
    SetKeywordsResponse,
    UserProfileSchema,
)
from .service import LearnoraContentDiscovery

router = APIRouter(prefix="/content-discovery", tags=["content-discovery"])

# Global service instance (singleton pattern for in-memory vector DB)
_discovery_service: LearnoraContentDiscovery | None = None


def get_discovery_service() -> LearnoraContentDiscovery:
    """Get or create the content discovery service instance."""
    global _discovery_service
    if _discovery_service is None:
        _discovery_service = LearnoraContentDiscovery(
            enable_crawler=True,
            enable_api_fetcher=True,
            enable_nlp=True,
        )
    return _discovery_service


@router.post("/search", response_model=SearchResponse)
async def search_content(
    request: SearchRequest,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Dict:
    """
    Search for learning content with personalization and NLP.
    
    - **query**: Natural language search query
    - **strategy**: Search strategy (bm25, dense, or hybrid)
    - **top_k**: Number of results to return
    - **use_nlp**: Enable NLP query processing
    - **personalize**: Enable content personalization (summaries, highlights)
    - **max_summary_words**: Maximum words for personalized summaries
    """
    service = get_discovery_service()
    
    # Build user profile from stored preferences (evolving system!)
    pref_service = PreferenceService(db)
    user_profile = await pref_service.build_user_profile(user.id)
    
    try:
        results = service.discover_and_personalize(
            query=request.query,
            user_profile=user_profile,
            strategy=request.strategy,
            top_k=request.top_k,
            refresh_content=request.refresh_content,
            auto_discover=request.auto_discover,
            discovery_sources=request.discovery_sources,
            use_nlp=request.use_nlp,
        )
        
        # 🆕 NEW: Apply content personalization if requested
        if request.personalize:
            personalization_service = get_personalization_service()
            
            for result in results['results']:
                try:
                    # Get user's preferred difficulty from profile
                    user_level = user_profile.knowledge_areas.get('preferred_difficulty', 'intermediate')
                    if not user_level or user_level not in ['beginner', 'intermediate', 'advanced', 'expert']:
                        user_level = 'intermediate'
                    
                    # Get content from result (it's a dict)
                    content = result['content']
                    content_type = content.get('content_type', 'article')
                    
                    # Personalize the content
                    personalized = personalization_service.personalize_content(
                        content=content,
                        user_level=user_level,
                        max_summary_words=request.max_summary_words,
                        user_time_budget=user_profile.available_time_daily,
                        include_highlights=content_type.lower() in ['video', 'tutorial'],
                    )
                    
                    # Add personalized fields to result
                    result['personalized_summary'] = personalized.personalized_summary
                    result['tldr'] = personalized.tldr
                    result['key_takeaways'] = personalized.key_takeaways
                    result['estimated_time'] = personalized.estimated_time
                    
                    # Convert highlights to dict format
                    if personalized.highlights:
                        result['highlights'] = [
                            {
                                'timestamp': h.timestamp,
                                'topic': h.topic,
                                'description': h.description,
                                'importance_score': h.importance_score,
                            }
                            for h in personalized.highlights
                        ]
                    
                except Exception as e:
                    # Log error but don't fail the whole request
                    content_id = result.get('content', {}).get('id', 'unknown')
                    logging.error(f"Failed to personalize content {content_id}: {e}")
                    # Keep original content without personalization
        
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.post("/crawl", response_model=CrawlResponse)
async def crawl_urls(
    request: CrawlRequest,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Dict:
    """
    Crawl URLs and add discovered content to the index.
    
    - **urls**: List of URLs to crawl
    - **custom_keywords**: Optional custom keywords for tag extraction
      (e.g., ["react", "vue", "angular", "typescript"])
    """
    service = get_discovery_service()
    
    try:
        # Update custom keywords if provided
        if request.custom_keywords:
            service.set_custom_keywords(request.custom_keywords)
        
        discovered_count = service.crawl_and_index_urls(request.urls)
        total_indexed = len(service.vector_db.contents)
        
        return {
            "discovered_count": discovered_count,
            "total_indexed": total_indexed,
        }
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Crawl failed: {str(e)}")


@router.post("/index", response_model=IndexContentResponse)
async def index_content(
    request: IndexContentRequest,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Dict:
    """
    Manually index learning content.
    
    - **contents**: List of learning content items to index
    """
    service = get_discovery_service()
    
    try:
        # Convert schemas to dataclass instances
        contents = [
            LearningContent(**content.model_dump())
            for content in request.contents
        ]
        
        service.vector_db.add_contents(contents)
        
        return {
            "indexed_count": len(contents),
            "total_indexed": len(service.vector_db.contents),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Indexing failed: {str(e)}")


@router.get("/stats")
async def get_stats(
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Dict:
    """Get content discovery statistics."""
    service = get_discovery_service()
    
    return {
        "total_indexed": len(service.vector_db.contents),
        "crawler_enabled": service.crawler is not None,
        "api_fetcher_enabled": service.api_fetcher is not None,
        "nlp_enabled": service.nlp is not None,
        "auto_discovery_enabled": service._auto_discovery_enabled,
    }


@router.post("/enable-auto-discovery")
async def enable_auto_discovery(
    enabled: bool = True,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Dict:
    """Enable or disable automatic content discovery."""
    service = get_discovery_service()
    service.enable_auto_discovery(enabled)
    
    return {
        "auto_discovery_enabled": service._auto_discovery_enabled,
    }


@router.post("/set-keywords", response_model=SetKeywordsResponse)
async def set_custom_keywords(
    request: SetKeywordsRequest,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Dict:
    """
    Set custom keywords for dynamic tag extraction during crawling.
    
    - **keywords**: List of custom keywords (e.g., ["react", "nextjs", "typescript", "tailwind"])
    
    These keywords will be used to extract tags when crawling URLs.
    The crawler will also use dynamic extraction based on:
    - Capitalized words (technology names)
    - Frequently occurring words
    - Hashtags
    """
    service = get_discovery_service()
    service.set_custom_keywords(request.keywords)
    
    return {
        "keywords": request.keywords,
        "count": len(request.keywords),
        "message": f"Successfully set {len(request.keywords)} custom keywords for tag extraction",
    }


@router.get("/content/{content_id}", response_model=LearningContentSchema)
async def get_content(
    content_id: str,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
) -> LearningContentSchema:
    """Get a specific content item by ID."""
    service = get_discovery_service()
    
    content = service.vector_db.contents.get(content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    return LearningContentSchema(**content.__dict__)


@router.get("/contents", response_model=List[LearningContentSchema])
async def list_contents(
    skip: int = 0,
    limit: int = 100,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
) -> List[LearningContentSchema]:
    """List all indexed content items."""
    service = get_discovery_service()
    
    contents = list(service.vector_db.contents.values())
    paginated = contents[skip : skip + limit]
    
    return [LearningContentSchema(**content.__dict__) for content in paginated]
