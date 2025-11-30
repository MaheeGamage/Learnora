"""API content fetcher for external educational platforms."""

from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import datetime
from typing import Dict, List, Optional
from urllib.parse import quote_plus

import feedparser
import requests
from ddgs import DDGS

from .models import LearningContent


class APIContentFetcher:
    """
    Fetch and analyze content from multiple educational sources.
    
    Supports:
    - YouTube Data API (videos)
    - DuckDuckGo Search (web articles, tutorials)
    - Medium RSS (articles)
    - Gemini API (content analysis and metadata extraction)
    """

    def __init__(self, api_keys: Optional[Dict[str, str]] = None):
        self.api_keys = api_keys or {}
        
        # Get API keys from environment or config
        self.youtube_api_key = self.api_keys.get('youtube') or os.getenv('YOUTUBE_API_KEY')
        self.perplexity_api_key = self.api_keys.get('perplexity') or os.getenv('PERPLEXITY_API_KEY')
        
        # Initialize Perplexity AI if available
        self.perplexity_enabled = False
        if self.perplexity_api_key:
            self.perplexity_enabled = True
            print("✅ Perplexity AI initialized for content analysis")
        
        # Educational domains to prioritize
        self.educational_domains = [
            'medium.com', 'dev.to', 'realpython.com', 'freecodecamp.org',
            'codecademy.com', 'tutorialspoint.com', 'geeksforgeeks.org',
            'w3schools.com', 'mdn.mozilla.org', 'stackoverflow.com'
        ]

    def fetch_youtube_content(self, query: str, max_results: int = 10) -> List[LearningContent]:
        """
        Fetch educational videos from YouTube using YouTube Data API v3.
        
        Requires YOUTUBE_API_KEY environment variable.
        Free tier: 10,000 units/day (100 searches)
        """
        if not self.youtube_api_key:
            print("⚠️ YouTube API key not configured - skipping YouTube search")
            return []
        
        try:
            url = "https://www.googleapis.com/youtube/v3/search"
            params = {
                'part': 'snippet',
                'q': query,
                'type': 'video',
                'videoCategoryId': '27',  # Education category
                'maxResults': min(max_results, 10),
                'key': self.youtube_api_key,
                'order': 'relevance',
                'relevanceLanguage': 'en'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            contents = []
            for item in data.get('items', []):
                video_id = item['id']['videoId']
                snippet = item['snippet']
                
                # Get video duration and stats
                duration = self._get_youtube_duration(video_id)
                
                content = LearningContent(
                    id=f"youtube_{video_id}",
                    title=snippet['title'],
                    description=snippet['description'][:500],  # Truncate long descriptions
                    content_type='video',
                    source='YouTube',
                    url=f"https://www.youtube.com/watch?v={video_id}",
                    difficulty=self._infer_difficulty(snippet['title'], snippet['description']),
                    duration_minutes=duration,
                    tags=self._extract_tags(snippet['title'] + ' ' + snippet['description']),
                    metadata={
                        'channel': snippet['channelTitle'],
                        'published_at': snippet['publishedAt'],
                        'thumbnail': snippet['thumbnails']['high']['url']
                    },
                    checksum=hashlib.md5(f"youtube_{video_id}".encode()).hexdigest()
                )
                
                # Enhance with Perplexity if available
                if self.perplexity_enabled:
                    content = self._enhance_with_perplexity(content)
                
                contents.append(content)
            
            print(f"✅ Fetched {len(contents)} YouTube videos for '{query}'")
            return contents
            
        except Exception as e:
            print(f"❌ YouTube fetch error: {e}")
            return []

    def _get_youtube_duration(self, video_id: str) -> int:
        """Get video duration in minutes from YouTube API."""
        if not self.youtube_api_key:
            return 0
        
        try:
            url = "https://www.googleapis.com/youtube/v3/videos"
            params = {
                'part': 'contentDetails',
                'id': video_id,
                'key': self.youtube_api_key
            }
            
            response = requests.get(url, params=params, timeout=5)
            data = response.json()
            
            if data.get('items'):
                duration_str = data['items'][0]['contentDetails']['duration']
                # Parse ISO 8601 duration (e.g., "PT15M30S")
                minutes = self._parse_duration(duration_str)
                return minutes
        except:
            pass
        
        return 0

    def _parse_duration(self, duration: str) -> int:
        """Parse ISO 8601 duration to minutes."""
        match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
        if not match:
            return 0
        
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)
        
        return hours * 60 + minutes + (1 if seconds > 30 else 0)

    def fetch_medium_content(self, query: str, max_results: int = 10) -> List[LearningContent]:
        """
        Fetch articles from Medium using RSS feeds.
        
        No API key required - uses public RSS feeds.
        Searches by tag and topic.
        """
        try:
            contents = []
            
            # Clean query for URL
            query_tag = query.lower().replace(' ', '-')
            
            # Try multiple Medium feed URLs
            feed_urls = [
                f'https://medium.com/feed/tag/{query_tag}',
                f'https://medium.com/feed/topic/{query_tag}',
            ]
            
            for feed_url in feed_urls:
                try:
                    feed = feedparser.parse(feed_url)
                    
                    for entry in feed.entries[:max_results]:
                        # Extract clean text from HTML summary
                        description = self._clean_html(entry.get('summary', ''))[:500]
                        
                        content = LearningContent(
                            id=f"medium_{hashlib.md5(entry.link.encode()).hexdigest()[:16]}",
                            title=entry.title,
                            description=description,
                            content_type='article',
                            source='Medium',
                            url=entry.link,
                            difficulty=self._infer_difficulty(entry.title, description),
                            duration_minutes=self._estimate_reading_time(description),
                            tags=self._extract_tags(entry.title + ' ' + description),
                            metadata={
                                'author': entry.get('author', 'Unknown'),
                                'published_at': entry.get('published', '')
                            },
                            checksum=hashlib.md5(entry.link.encode()).hexdigest()
                        )
                        
                        # Enhance with Perplexity if available
                        if self.perplexity_enabled:
                            content = self._enhance_with_perplexity(content)
                        
                        contents.append(content)
                    
                    if contents:
                        break  # Found content, no need to try other feeds
                        
                except Exception as e:
                    continue
            
            print(f"✅ Fetched {len(contents)} Medium articles for '{query}'")
            return contents[:max_results]
            
        except Exception as e:
            print(f"❌ Medium fetch error: {e}")
            return []

    def fetch_github_content(self, query: str, max_results: int = 10) -> List[LearningContent]:
        """
        Fetch educational repositories and documentation from GitHub.
        
        Uses DuckDuckGo to search GitHub (no API key needed).
        Focuses on repos with tutorials, documentation, and learning resources.
        """
        try:
            # Search GitHub via DuckDuckGo
            search_query = f"site:github.com {query} tutorial OR documentation OR guide"
            
            with DDGS() as ddgs:
                results = ddgs.text(search_query, max_results=max_results)
                
                contents = []
                for result in results:
                    # Filter for actual GitHub repo URLs
                    if 'github.com' not in result['href']:
                        continue
                    
                    content = LearningContent(
                        id=f"github_{hashlib.md5(result['href'].encode()).hexdigest()[:16]}",
                        title=result['title'],
                        description=result['body'][:500],
                        content_type='documentation',
                        source='GitHub',
                        url=result['href'],
                        difficulty=self._infer_difficulty(result['title'], result['body']),
                        duration_minutes=self._estimate_reading_time(result['body']),
                        tags=self._extract_tags(result['title'] + ' ' + result['body']),
                        metadata={
                            'snippet': result['body'][:200]
                        },
                        checksum=hashlib.md5(result['href'].encode()).hexdigest()
                    )
                    
                    # Enhance with Perplexity if available
                    if self.perplexity_enabled:
                        content = self._enhance_with_perplexity(content)
                    
                    contents.append(content)
                
                print(f"✅ Fetched {len(contents)} GitHub resources for '{query}'")
                return contents
                
        except Exception as e:
            print(f"❌ GitHub fetch error: {e}")
            return []

    def fetch_coursera_content(self, query: str, max_results: int = 10) -> List[LearningContent]:
        """
        Search for educational content using DuckDuckGo.
        
        Focuses on high-quality educational domains like:
        - FreeCodeCamp, Real Python, GeeksForGeeks
        - MDN, W3Schools, Tutorialspoint
        - Dev.to, Stack Overflow, Medium
        
        No API key required - completely free.
        """
        try:
            with DDGS() as ddgs:
                # Search with educational focus
                search_query = f"{query} tutorial OR guide OR learn"
                results = ddgs.text(search_query, max_results=max_results * 2)  # Get more to filter
                
                contents = []
                for result in results:
                    # Prioritize educational domains
                    is_educational = any(domain in result['href'] for domain in self.educational_domains)
                    
                    # Determine content type from URL
                    content_type = self._classify_content_type(result['href'], result['title'])
                    
                    content = LearningContent(
                        id=f"web_{hashlib.md5(result['href'].encode()).hexdigest()[:16]}",
                        title=result['title'],
                        description=result['body'][:500],
                        content_type=content_type,
                        source=self._extract_domain(result['href']),
                        url=result['href'],
                        difficulty=self._infer_difficulty(result['title'], result['body']),
                        duration_minutes=self._estimate_reading_time(result['body']),
                        tags=self._extract_tags(result['title'] + ' ' + result['body']),
                        metadata={
                            'is_educational': is_educational,
                            'snippet': result['body'][:200]
                        },
                        checksum=hashlib.md5(result['href'].encode()).hexdigest()
                    )
                    
                    # Enhance with Perplexity if available
                    if self.perplexity_enabled:
                        content = self._enhance_with_perplexity(content)
                    
                    contents.append(content)
                    
                    if len(contents) >= max_results:
                        break
                
                # Sort by educational quality
                contents.sort(key=lambda x: x.metadata.get('is_educational', False), reverse=True)
                
                print(f"✅ Fetched {len(contents)} web resources for '{query}'")
                return contents[:max_results]
                
        except Exception as e:
            print(f"❌ DuckDuckGo fetch error: {e}")
            return []

    def _enhance_with_perplexity(self, content: LearningContent) -> LearningContent:
        """
        Use Perplexity AI to analyze and enhance content metadata.
        
        Extracts:
        - More accurate difficulty level
        - Better tags/keywords
        - Learning outcomes
        - Content quality score
        """
        if not self.perplexity_enabled:
            return content
        
        try:
            prompt = f"""Analyze this learning resource and extract metadata as JSON:

Title: {content.title}
Description: {content.description}
Type: {content.content_type}

Extract:
1. difficulty: "beginner", "intermediate", "advanced", or "expert"
2. tags: 5-8 relevant keywords (lowercase, no duplicates)
3. quality_score: 1-10 (based on title/description quality)
4. learning_outcomes: 3 brief bullet points (what learner will gain)

Return ONLY valid JSON with these exact keys."""
            
            # Call Perplexity API
            headers = {
                'Authorization': f'Bearer {self.perplexity_api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': 'sonar',  # Lightweight, cost-effective search model
                'messages': [
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'temperature': 0.2,
                'max_tokens': 500
            }
            
            response = requests.post(
                'https://api.perplexity.ai/chat/completions',
                headers=headers,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            
            result = response.json()
            analysis_text = result['choices'][0]['message']['content']
            analysis = self._parse_ai_json(analysis_text)
            
            if analysis:
                # Update content with Perplexity analysis
                content.difficulty = analysis.get('difficulty', content.difficulty)
                content.tags = analysis.get('tags', content.tags)[:10]  # Limit to 10 tags
                
                # Add quality score and outcomes to metadata
                content.metadata.update({
                    'quality_score': analysis.get('quality_score', 7),
                    'learning_outcomes': analysis.get('learning_outcomes', []),
                    'ai_analyzed': True
                })
            
        except Exception as e:
            # Don't fail if Perplexity analysis fails - just use original content
            print(f"⚠️ Perplexity analysis skipped: {e}")
        
        return content

    def _parse_ai_json(self, text: str) -> Optional[Dict]:
        """Extract JSON from AI response (handles markdown code blocks)."""
        """Extract JSON from Gemini response (handles markdown code blocks)."""
        try:
            # Remove markdown code blocks if present
            text = text.strip()
            if text.startswith('```'):
                text = re.sub(r'```(?:json)?\n?', '', text)
            
            return json.loads(text)
        except:
            return None

    def _infer_difficulty(self, title: str, description: str) -> str:
        """Infer difficulty level from title and description."""
        text = (title + ' ' + description).lower()
        
        if any(word in text for word in ['beginner', 'intro', 'basics', 'getting started', 'start']):
            return 'beginner'
        elif any(word in text for word in ['advanced', 'expert', 'master', 'deep dive']):
            return 'advanced'
        elif any(word in text for word in ['intermediate', 'beyond basics']):
            return 'intermediate'
        
        return 'intermediate'

    def _extract_tags(self, text: str) -> List[str]:
        """Extract relevant tags from text."""
        text = text.lower()
        
        # Common tech keywords
        keywords = [
            'python', 'javascript', 'java', 'react', 'node', 'typescript',
            'machine learning', 'ai', 'data science', 'web development',
            'backend', 'frontend', 'database', 'api', 'tutorial', 'guide'
        ]
        
        tags = [keyword for keyword in keywords if keyword in text]
        
        # Add more specific tags using regex
        words = re.findall(r'\b[a-z]{4,}\b', text)
        word_freq = {}
        for word in words:
            if word not in ['this', 'that', 'with', 'from', 'have', 'will']:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Add top frequent words
        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
        tags.extend([word for word, _ in top_words])
        
        return list(set(tags))[:10]  # Remove duplicates, limit to 10

    def _estimate_reading_time(self, text: str) -> int:
        """Estimate reading time in minutes (200 words/min)."""
        words = len(text.split())
        return max(1, words // 200)

    def _classify_content_type(self, url: str, title: str) -> str:
        """Classify content type from URL and title."""
        url_lower = url.lower()
        title_lower = title.lower()
        
        if 'youtube.com' in url_lower or 'youtu.be' in url_lower:
            return 'video'
        elif 'github.com' in url_lower:
            return 'documentation'
        elif any(word in title_lower for word in ['tutorial', 'guide', 'how to']):
            return 'tutorial'
        elif any(word in url_lower for word in ['blog', 'article', 'medium']):
            return 'article'
        elif any(word in url_lower for word in ['course', 'class', 'lesson']):
            return 'course'
        
        return 'article'

    def _extract_domain(self, url: str) -> str:
        """Extract clean domain name from URL."""
        match = re.search(r'https?://(?:www\.)?([^/]+)', url)
        if match:
            domain = match.group(1)
            return domain.replace('.com', '').replace('.org', '').title()
        return 'Web'

    def _clean_html(self, html: str) -> str:
        """Remove HTML tags from text."""
        clean = re.sub(r'<[^>]+>', '', html)
        clean = re.sub(r'\s+', ' ', clean)
        return clean.strip()
