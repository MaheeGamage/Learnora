"""Content discovery service with personalization and NLP."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict, List, Optional, Sequence, Tuple

from .api_fetcher import APIContentFetcher
from .crawler import ContentCrawler
from .models import LearningContent, UserProfile
from .nlp import NaturalLanguageProcessor
from .vector_db import VectorDBManager


class LearnoraContentDiscovery:
    """Content discovery service combining search with personalization and NLP."""

    def __init__(
        self,
        *,
        vector_db: Optional[VectorDBManager] = None,
        openai_api_key: Optional[str] = None,
        redis_url: Optional[str] = None,
        enable_crawler: bool = True,
        enable_api_fetcher: bool = True,
        enable_nlp: bool = True,
        custom_keywords: Optional[List[str]] = None,
    ) -> None:
        self.vector_db = vector_db or VectorDBManager()
        self.openai_api_key = openai_api_key
        self.redis_url = redis_url
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.custom_keywords = custom_keywords  # User-provided keywords
        
        # Dynamic content discovery components
        self.crawler = ContentCrawler(custom_keywords=custom_keywords) if enable_crawler else None
        self.api_fetcher = APIContentFetcher({"openai": openai_api_key}) if enable_api_fetcher else None
        self._auto_discovery_enabled = False
        
        # Natural Language Processing
        self.nlp = NaturalLanguageProcessor() if enable_nlp else None

    def _cache_key(self, query: str, user_profile: UserProfile, strategy: str) -> str:
        profile_dict = asdict(user_profile)
        return f"{query}|{strategy}|{sorted(profile_dict.items())}"

    def enable_auto_discovery(self, enabled: bool = True) -> None:
        """Enable or disable automatic content discovery."""
        self._auto_discovery_enabled = enabled
    
    def set_custom_keywords(self, keywords: List[str]) -> None:
        """
        Set custom keywords for dynamic tag extraction.
        
        Args:
            keywords: List of keywords to use for tag extraction during crawling
        """
        self.custom_keywords = keywords
        if self.crawler:
            self.crawler.custom_keywords = keywords

    def crawl_and_index_urls(self, urls: List[str]) -> int:
        """Crawl URLs and add discovered content to the index."""
        if not self.crawler:
            raise RuntimeError("Crawler is not enabled")
        
        contents = self.crawler.crawl_urls(urls)
        if contents:
            self.vector_db.add_contents(contents)
        return len(contents)

    def fetch_and_index_from_apis(self, query: str, sources: Optional[List[str]] = None) -> int:
        """Fetch content from external APIs and add to index."""
        if not self.api_fetcher:
            raise RuntimeError("API fetcher is not enabled")
        
        sources = sources or ["youtube", "medium", "github"]
        all_contents = []
        
        for source in sources:
            if source == "youtube":
                all_contents.extend(self.api_fetcher.fetch_youtube_content(query))
            elif source == "medium":
                all_contents.extend(self.api_fetcher.fetch_medium_content(query))
            elif source == "github":
                all_contents.extend(self.api_fetcher.fetch_github_content(query))
            elif source == "coursera":
                all_contents.extend(self.api_fetcher.fetch_coursera_content(query))
        
        if all_contents:
            self.vector_db.add_contents(all_contents)
        return len(all_contents)

    def discover_and_personalize(
        self,
        query: str,
        user_profile: UserProfile,
        *,
        strategy: str = "hybrid",
        top_k: int = 5,
        refresh_content: bool = False,
        auto_discover: Optional[bool] = None,
        discovery_sources: Optional[List[str]] = None,
        use_nlp: bool = True,
    ) -> Dict[str, Any]:
        """
        Discover and personalize content with optional automatic content discovery and NLP.
        
        Args:
            query: Search query (natural language supported)
            user_profile: User profile for personalization
            strategy: Search strategy (bm25, dense, or hybrid)
            top_k: Number of results to return
            refresh_content: Whether to bypass cache
            auto_discover: Whether to automatically discover new content (overrides instance setting)
            discovery_sources: List of sources to discover from (e.g., ["youtube", "medium"])
            use_nlp: Whether to use NLP processing on the query
        """
        # Process query with NLP if enabled
        nlp_results = None
        processed_query = query
        
        if use_nlp and self.nlp:
            nlp_results = self.nlp.process_query(query)
            processed_query = nlp_results["expanded_query"]
            
            # Update user profile based on NLP entities
            entities = nlp_results["entities"]
            if entities["formats"] and not user_profile.preferred_formats:
                user_profile.preferred_formats = entities["formats"]
        
        # Auto-discover new content if enabled
        if auto_discover is None:
            auto_discover = self._auto_discovery_enabled
        
        if auto_discover and self.api_fetcher:
            try:
                # Use expanded query for better discovery
                new_count = self.fetch_and_index_from_apis(processed_query, discovery_sources)
                if new_count > 0:
                    refresh_content = True  # Force refresh if new content was added
            except Exception as e:
                print(f"Auto-discovery failed: {e}")
        
        if not refresh_content:
            cached = self._cache.get(self._cache_key(processed_query, user_profile, strategy))
            if cached is not None:
                # Add NLP info to cached results if available
                if nlp_results:
                    cached["nlp_analysis"] = nlp_results
                return cached

        # Search with processed query
        ranked = self.vector_db.search(processed_query, top_k=top_k, strategy=strategy)
        
        # Apply NLP-based filtering if we have entities
        if nlp_results and nlp_results["entities"]["difficulty"]:
            preferred_difficulty = nlp_results["entities"]["difficulty"][0]
            ranked = self._filter_by_difficulty(ranked, preferred_difficulty)
        
        personalized = self._personalize_results(ranked, user_profile)
        
        payload = {
            "query": query,
            "processed_query": processed_query if use_nlp else query,
            "user_id": user_profile.user_id,
            "strategy": strategy,
            "results": personalized,
            "stats": {
                "total_indexed": len(self.vector_db.contents),
                "returned": len(personalized),
            },
        }
        
        # Add NLP analysis to response
        if nlp_results:
            payload["nlp_analysis"] = {
                "intent": nlp_results["intent"],
                "entities": nlp_results["entities"],
                "key_terms": nlp_results["key_terms"],
            }
        
        self._cache[self._cache_key(processed_query, user_profile, strategy)] = payload
        return payload
    
    def _filter_by_difficulty(
        self,
        ranked_results: List[Tuple[LearningContent, float]],
        preferred_difficulty: str,
    ) -> List[Tuple[LearningContent, float]]:
        """Filter and boost results matching preferred difficulty."""
        filtered = []
        for content, score in ranked_results:
            if content.difficulty == preferred_difficulty:
                # Boost matching difficulty
                filtered.append((content, score * 1.2))
            else:
                # Keep but with lower priority
                filtered.append((content, score * 0.9))
        
        # Re-sort by adjusted scores
        filtered.sort(key=lambda x: x[1], reverse=True)
        return filtered

    def _personalize_results(
        self,
        ranked_results: Sequence[Tuple[LearningContent, float]],
        user_profile: UserProfile,
    ) -> List[Dict[str, Any]]:
        if not ranked_results:
            return []

        boost_formats = {fmt.lower() for fmt in user_profile.preferred_formats}
        available_time = user_profile.available_time_daily

        adjusted: List[Tuple[LearningContent, float]] = []
        for content, score in ranked_results:
            adjusted_score = score
            if boost_formats and content.content_type.lower() in boost_formats:
                adjusted_score *= 1.1
            if available_time and content.duration_minutes <= available_time:
                adjusted_score *= 1.05
            adjusted.append((content, adjusted_score))

        adjusted.sort(key=lambda item: item[1], reverse=True)
        result_payload: List[Dict[str, Any]] = []
        for content, score in adjusted:
            result_payload.append(
                {
                    "content": {
                        "id": content.id,
                        "title": content.title,
                        "url": content.url,
                        "description": content.description,
                        "content_type": content.content_type,
                        "source": content.source,
                        "difficulty": content.difficulty,
                        "duration_minutes": content.duration_minutes,
                        "tags": content.tags,
                        "prerequisites": content.prerequisites,
                        "metadata": content.metadata,
                        "created_at": content.created_at.isoformat(),
                        "checksum": content.checksum,
                    },
                    "score": round(score, 6),
                    "relevance_score": round(score, 6),
                    "personalization_boost": 0.0,
                }
            )
        return result_payload
