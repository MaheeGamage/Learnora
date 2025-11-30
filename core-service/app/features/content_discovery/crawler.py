"""Web crawler for content discovery."""

from __future__ import annotations

import hashlib
import gzip
from html.parser import HTMLParser
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse
from urllib.request import urlopen, Request

from .models import LearningContent


class ContentParser(HTMLParser):
    """Simple HTML parser to extract text and metadata from web pages."""

    def __init__(self):
        super().__init__()
        self.title = ""
        self.description = ""
        self.text_content = []
        self.in_title = False
        self.in_description = False

    def handle_starttag(self, tag, attrs):
        if tag == "title":
            self.in_title = True
        elif tag == "meta":
            attrs_dict = dict(attrs)
            if attrs_dict.get("name") == "description":
                self.description = attrs_dict.get("content", "")

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False

    def handle_data(self, data):
        if self.in_title:
            self.title = data.strip()
        elif data.strip():
            self.text_content.append(data.strip())

    def get_text(self) -> str:
        return " ".join(self.text_content)


class ContentCrawler:
    """Web crawler to dynamically discover learning content."""

    def __init__(
        self, 
        timeout: int = 10, 
        user_agent: str = "LearnoraBot/1.0",
        custom_keywords: Optional[List[str]] = None
    ):
        self.timeout = timeout
        self.user_agent = user_agent
        self.custom_keywords = custom_keywords  # User-provided keywords for tag extraction
        self._visited_urls = set()

    def fetch_url(self, url: str) -> Optional[str]:
        """Fetch content from a URL."""
        try:
            request = Request(url, headers={
                "User-Agent": self.user_agent,
                "Accept-Encoding": "gzip, deflate",
            })
            with urlopen(request, timeout=self.timeout) as response:
                if response.status == 200:
                    content_type = response.headers.get("Content-Type", "")
                    if "text/html" in content_type or "text/plain" in content_type:
                        # Read raw bytes
                        raw_data = response.read()
                        
                        # Try to decompress if gzip
                        try:
                            raw_data = gzip.decompress(raw_data)
                        except:
                            pass  # Not gzipped, use as-is
                        
                        # Decode to string
                        return raw_data.decode("utf-8", errors="ignore")
            return None
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

    def parse_html(self, html_content: str) -> Dict[str, Any]:
        """Parse HTML content and extract metadata."""
        parser = ContentParser()
        parser.feed(html_content)
        return {
            "title": parser.title,
            "description": parser.description,
            "text": parser.get_text()[:500],  # First 500 chars
        }

    def extract_tags(self, text: str, max_tags: int = 10, custom_keywords: Optional[List[str]] = None) -> List[str]:
        """
        Extract tags from text using dynamic keyword extraction.
        
        Args:
            text: Text to extract tags from
            max_tags: Maximum number of tags to return
            custom_keywords: Optional custom keywords to search for (user-provided)
        
        Returns:
            List of extracted tags
        """
        import re
        from collections import Counter
        
        # Stop words to filter out (common words with no semantic value)
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
            "of", "with", "by", "from", "as", "is", "was", "are", "were", "been",
            "be", "have", "has", "had", "do", "does", "did", "will", "would", "should",
            "could", "may", "might", "must", "can", "this", "that", "these", "those",
            "it", "its", "they", "them", "their", "what", "which", "who", "when",
            "where", "why", "how", "all", "each", "every", "both", "few", "more",
            "most", "other", "some", "such", "no", "nor", "not", "only", "own",
            "same", "so", "than", "too", "very", "just", "about", "into", "through",
            "during", "before", "after", "above", "below", "between", "under", "again",
            "also", "another", "any", "because", "become", "become", "already", "always",
            "something", "someone", "somewhere", "still", "take", "then", "there", "though",
            "thus", "together", "unless", "until", "upon", "using", "via", "want",
            "well", "whether", "while", "within", "without", "yet", "your"
        }
        
        # Use custom keywords if provided, otherwise rely on dynamic extraction only
        search_keywords = set(custom_keywords) if custom_keywords else set()
        
        text_lower = text.lower()
        tags = []
        
        # 1. Extract keywords that appear in the text
        for keyword in search_keywords:
            if keyword in text_lower:
                tags.append(keyword)
        
        # 2. Extract capitalized words (likely important terms)
        # Match words that start with capital letter (potential proper nouns/technologies)
        capitalized_pattern = r'\b[A-Z][a-z]+(?:[A-Z][a-z]+)*\b'
        capitalized_words = re.findall(capitalized_pattern, text)
        
        # Filter and add capitalized words
        for word in capitalized_words:
            word_lower = word.lower()
            if (word_lower not in stop_words and 
                len(word) > 2 and 
                word not in tags and
                len(tags) < max_tags):
                tags.append(word_lower)
        
        # 3. Extract frequently occurring words (dynamic tag discovery)
        # Tokenize and count words
        words = re.findall(r'\b[a-z]{3,}\b', text_lower)
        word_freq = Counter(word for word in words if word not in stop_words)
        
        # Add top frequent words as tags
        for word, count in word_freq.most_common(max_tags - len(tags)):
            if count >= 2 and word not in tags:  # Word appears at least twice
                tags.append(word)
        
        # 4. Extract hashtags if present
        hashtags = re.findall(r'#(\w+)', text)
        for tag in hashtags:
            tag_lower = tag.lower()
            if tag_lower not in tags and len(tags) < max_tags:
                tags.append(tag_lower)
        
        # Return unique tags, limited to max_tags
        return list(dict.fromkeys(tags))[:max_tags]

    def crawl_url(self, url: str, content_id: Optional[str] = None) -> Optional[LearningContent]:
        """Crawl a single URL and create a LearningContent object."""
        if url in self._visited_urls:
            return None
        
        self._visited_urls.add(url)
        html = self.fetch_url(url)
        
        if not html:
            return None
        
        parsed = self.parse_html(html)
        
        if not parsed["title"]:
            return None
        
        # Generate checksum for deduplication
        checksum = hashlib.md5(parsed["text"].encode()).hexdigest()
        
        # Extract domain as source
        domain = urlparse(url).netloc
        
        # Estimate difficulty and duration (simple heuristics)
        text = parsed["text"].lower()
        difficulty = "intermediate"
        if "beginner" in text or "introduction" in text or "basics" in text:
            difficulty = "beginner"
        elif "advanced" in text or "expert" in text or "master" in text:
            difficulty = "advanced"
        
        # Estimate duration based on text length
        word_count = len(parsed["text"].split())
        duration_minutes = max(5, min(120, word_count // 50))
        
        # Extract tags dynamically (use custom keywords if provided)
        tags = self.extract_tags(
            parsed["title"] + " " + parsed["description"],
            max_tags=10,
            custom_keywords=self.custom_keywords
        )
        
        content_id = content_id or hashlib.md5(url.encode()).hexdigest()[:12]
        
        return LearningContent(
            id=content_id,
            title=parsed["title"],
            content_type="article",
            source=domain,
            url=url,
            description=parsed["description"] or parsed["text"][:200],
            difficulty=difficulty,
            duration_minutes=duration_minutes,
            tags=tags,
            checksum=checksum,
        )

    def crawl_urls(self, urls: List[str]) -> List[LearningContent]:
        """Crawl multiple URLs and return discovered content."""
        results = []
        for url in urls:
            content = self.crawl_url(url)
            if content:
                results.append(content)
        return results
