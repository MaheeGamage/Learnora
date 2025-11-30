"""Pydantic schemas for content discovery API."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class LearningContentSchema(BaseModel):
    """Schema for learning content."""
    
    id: str
    title: str
    content_type: str
    source: str
    url: str
    description: str
    difficulty: str
    duration_minutes: int
    tags: List[str] = Field(default_factory=list)
    prerequisites: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    checksum: Optional[str] = None

    model_config = {"from_attributes": True}


class UserProfileSchema(BaseModel):
    """Schema for user profile."""
    
    user_id: str
    knowledge_areas: Dict[str, str] = Field(default_factory=dict)
    learning_goals: List[str] = Field(default_factory=list)
    preferred_formats: List[str] = Field(default_factory=list)
    available_time_daily: int = 60
    learning_style: str = "balanced"

    model_config = {"from_attributes": True}


class SearchRequest(BaseModel):
    """Request schema for content search."""
    
    query: str = Field(..., description="Search query")
    strategy: str = Field(default="hybrid", description="Search strategy (bm25, dense, or hybrid)")
    top_k: int = Field(default=5, ge=1, le=50, description="Number of results to return")
    refresh_content: bool = Field(default=False, description="Bypass cache")
    auto_discover: Optional[bool] = Field(default=None, description="Enable auto discovery")
    discovery_sources: Optional[List[str]] = Field(default=None, description="Sources to discover from")
    use_nlp: bool = Field(default=True, description="Use NLP processing")
    
    # 🆕 Personalization options
    personalize: bool = Field(default=False, description="Enable content personalization")
    max_summary_words: int = Field(default=150, ge=50, le=300, description="Max words for personalized summaries")


class SearchResultItemSchema(BaseModel):
    """Schema for search result item."""
    
    content: LearningContentSchema
    score: float
    relevance_score: float
    personalization_boost: float
    
    # 🆕 Personalized content fields (optional)
    personalized_summary: Optional[str] = None
    tldr: Optional[str] = None
    key_takeaways: Optional[List[str]] = None
    highlights: Optional[List[Dict[str, Any]]] = None
    estimated_time: Optional[int] = None


class SearchResponse(BaseModel):
    """Response schema for content search."""
    
    query: str
    processed_query: str
    user_id: str
    strategy: str
    results: List[SearchResultItemSchema]
    stats: Dict[str, int]
    nlp_analysis: Optional[Dict[str, Any]] = None


class CrawlRequest(BaseModel):
    """Request schema for URL crawling."""
    
    urls: List[str] = Field(..., description="List of URLs to crawl")
    custom_keywords: Optional[List[str]] = Field(
        default=None, 
        description="Custom keywords for tag extraction (e.g., ['react', 'vue', 'angular'])"
    )


class CrawlResponse(BaseModel):
    """Response schema for URL crawling."""
    
    discovered_count: int
    total_indexed: int


class IndexContentRequest(BaseModel):
    """Request schema for indexing content."""
    
    contents: List[LearningContentSchema]


class IndexContentResponse(BaseModel):
    """Response schema for indexing content."""
    
    indexed_count: int
    total_indexed: int


class SetKeywordsRequest(BaseModel):
    """Request schema for setting custom keywords."""
    
    keywords: List[str] = Field(
        ..., 
        description="List of custom keywords for tag extraction",
        min_length=1
    )


class SetKeywordsResponse(BaseModel):
    """Response schema for setting custom keywords."""
    
    keywords: List[str]
    count: int
    message: str
