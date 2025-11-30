"""Content Personalization Service for adaptive learning content transformation.

This service provides:
1. AI-powered content summarization based on user level
2. Video highlight extraction
3. Content difficulty adaptation
4. Time-constrained content personalization
"""

import json
import logging
import re
from typing import Dict, List, Optional

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage

from app.features.content_discovery.models import LearningContent
from .models import PersonalizedContent, VideoHighlight, ContentSummary

logger = logging.getLogger(__name__)


class ContentPersonalizationService:
    """Service for personalizing learning content based on user preferences and level."""
    
    def __init__(self, model_name: str = "gemini-2.0-flash-exp"):
        """Initialize the personalization service.
        
        Args:
            model_name: Name of the Gemini model to use
        """
        self.model = ChatGoogleGenerativeAI(model=model_name)
        logger.info(f"Initialized ContentPersonalizationService with {model_name}")
    
    def personalize_content(
        self,
        content: LearningContent,
        user_level: str = "intermediate",
        max_summary_words: int = 200,
        user_time_budget: Optional[int] = None,  # minutes
        include_highlights: bool = True,
    ) -> PersonalizedContent:
        """
        Personalize learning content for a specific user.
        
        Args:
            content: Original learning content
            user_level: User's skill level (beginner, intermediate, advanced, expert)
            max_summary_words: Maximum words for summary
            user_time_budget: User's available time in minutes
            include_highlights: Whether to extract video highlights
            
        Returns:
            PersonalizedContent with summaries, highlights, and adaptations
        """
        logger.info(f"Personalizing content '{content.title}' for {user_level} level")
        
        personalized = PersonalizedContent(
            content_id=content.id,
            original_title=content.title,
            original_description=content.description,
            adapted_difficulty=user_level,
        )
        
        # Generate personalized summary
        try:
            summary = self.generate_summary(
                content=content,
                user_level=user_level,
                max_words=max_summary_words
            )
            personalized.personalized_summary = summary.summary_text
            personalized.key_takeaways = summary.key_points
            personalized.tldr = self._generate_tldr(content, user_level)
        except Exception as e:
            logger.error(f"Failed to generate summary: {e}")
            personalized.personalized_summary = content.description
        
        # Extract video highlights if applicable
        if include_highlights and content.content_type.lower() in ["video", "tutorial"]:
            try:
                highlights = self.extract_video_highlights(
                    content=content,
                    max_duration=user_time_budget or content.duration_minutes,
                )
                personalized.highlights = highlights
            except Exception as e:
                logger.error(f"Failed to extract video highlights: {e}")
        
        # Calculate estimated time based on user level
        if user_time_budget:
            personalized.estimated_time = self._adjust_time_for_level(
                original_duration=content.duration_minutes,
                user_level=user_level,
                budget=user_time_budget,
            )
        
        personalized.personalization_level = "advanced"
        return personalized
    
    def generate_summary(
        self,
        content: LearningContent,
        user_level: str = "intermediate",
        max_words: int = 200,
    ) -> ContentSummary:
        """
        Generate a level-appropriate summary of the content.
        
        Args:
            content: Learning content to summarize
            user_level: Target user level
            max_words: Maximum words for summary
            
        Returns:
            ContentSummary with summarized text and key points
        """
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an expert educational content curator. 
Your job is to create clear, concise summaries of learning materials adapted to different skill levels.

For BEGINNER level:
- Use simple, non-technical language
- Explain concepts from first principles
- Include analogies and real-world examples
- Focus on "what" and "why" before "how"

For INTERMEDIATE level:
- Use standard technical terminology
- Assume basic foundational knowledge
- Balance theory with practical application
- Include some best practices

For ADVANCED level:
- Use advanced technical vocabulary
- Assume strong foundational knowledge
- Focus on nuances, edge cases, and advanced patterns
- Include performance and optimization considerations

For EXPERT level:
- Use precise technical language
- Assume deep expertise
- Focus on architectural decisions, trade-offs, and cutting-edge techniques
- Include references to research and advanced topics
"""),
            HumanMessage(content="""Summarize this {content_type} for a {user_level} learner in approximately {max_words} words.

Title: {title}
Description: {description}
Tags: {tags}
Difficulty: {difficulty}

Provide your response in JSON format:
{{
    "summary": "Your level-appropriate summary here",
    "key_points": ["Key point 1", "Key point 2", "Key point 3"]
}}""")
        ])
        
        # Invoke the model
        response = self.model.invoke(
            prompt.format_messages(
                content_type=content.content_type,
                user_level=user_level,
                max_words=max_words,
                title=content.title,
                description=content.description,
                tags=", ".join(content.tags),
                difficulty=content.difficulty,
            )
        )
        
        # Parse response
        result = self._extract_json_from_response(response.content)
        
        return ContentSummary(
            original_length=len(content.description.split()),
            summary_length=len(result.get("summary", "").split()),
            summary_text=result.get("summary", content.description),
            key_points=result.get("key_points", []),
            difficulty_level=user_level,
        )
    
    def extract_video_highlights(
        self,
        content: LearningContent,
        max_duration: int = 30,  # minutes
    ) -> List[VideoHighlight]:
        """
        Extract key moments/highlights from video content.
        
        Args:
            content: Video content to analyze
            max_duration: Maximum duration to fit highlights into
            
        Returns:
            List of VideoHighlight objects with timestamps and topics
        """
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an expert at analyzing educational video content and identifying key learning moments.
Your job is to extract the most important segments that a learner should focus on.

Identify 3-5 key moments that cover:
1. Core concepts introduction
2. Important examples or demonstrations
3. Critical insights or "aha!" moments
4. Practical applications
5. Summary or key takeaways

Provide realistic timestamps based on typical video pacing."""),
            HumanMessage(content="""Analyze this video and identify key moments to watch:

Title: {title}
Description: {description}
Duration: {duration} minutes
Topic: {tags}

Provide your response in JSON format with an array of highlights:
{{
    "highlights": [
        {{
            "timestamp": "MM:SS",
            "topic": "Brief topic name",
            "description": "What happens at this moment",
            "importance": 0.9
        }}
    ]
}}

Keep the total highlighted time under {max_duration} minutes.""")
        ])
        
        response = self.model.invoke(
            prompt.format_messages(
                title=content.title,
                description=content.description,
                duration=content.duration_minutes,
                tags=", ".join(content.tags[:5]),
                max_duration=max_duration,
            )
        )
        
        result = self._extract_json_from_response(response.content)
        highlights_data = result.get("highlights", [])
        
        return [
            VideoHighlight(
                timestamp=h.get("timestamp", "0:00"),
                topic=h.get("topic", "Key moment"),
                description=h.get("description", ""),
                importance_score=h.get("importance", 0.5),
            )
            for h in highlights_data
        ]
    
    def adapt_content_difficulty(
        self,
        text: str,
        current_level: str,
        target_level: str,
    ) -> str:
        """
        Adapt content from one difficulty level to another.
        
        Args:
            text: Original text content
            current_level: Current difficulty level
            target_level: Target difficulty level
            
        Returns:
            Adapted text at target level
        """
        if current_level == target_level:
            return text
        
        direction = "simplify" if self._level_order(target_level) < self._level_order(current_level) else "enhance"
        
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=f"""You are an expert educational content adapter.
Your job is to {direction} content to match a learner's skill level while preserving accuracy."""),
            HumanMessage(content="""Rewrite this {current_level}-level content for a {target_level} learner:

{text}

Maintain the same core information but adjust:
- Vocabulary complexity
- Sentence structure
- Depth of explanation
- Use of technical jargon
- Examples and analogies

Provide only the rewritten text, no additional commentary.""")
        ])
        
        response = self.model.invoke(
            prompt.format_messages(
                current_level=current_level,
                target_level=target_level,
                text=text,
            )
        )
        
        return response.content.strip()
    
    def _generate_tldr(self, content: LearningContent, user_level: str) -> str:
        """Generate a very brief TL;DR summary (1-2 sentences)."""
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="You are an expert at creating ultra-concise summaries."),
            HumanMessage(content="""Create a 1-2 sentence TL;DR for this content suitable for a {user_level} learner:

Title: {title}
Description: {description}

TL;DR:""")
        ])
        
        response = self.model.invoke(
            prompt.format_messages(
                user_level=user_level,
                title=content.title,
                description=content.description[:500],  # Limit for speed
            )
        )
        
        return response.content.strip()
    
    def _adjust_time_for_level(
        self,
        original_duration: int,
        user_level: str,
        budget: int,
    ) -> int:
        """
        Adjust estimated time based on user level.
        
        Beginners typically need more time, experts need less.
        """
        level_multipliers = {
            "beginner": 1.5,
            "intermediate": 1.0,
            "advanced": 0.8,
            "expert": 0.6,
        }
        
        multiplier = level_multipliers.get(user_level.lower(), 1.0)
        adjusted = int(original_duration * multiplier)
        
        # Respect budget constraint
        return min(adjusted, budget)
    
    def _level_order(self, level: str) -> int:
        """Get numeric order of difficulty level."""
        levels = {"beginner": 1, "intermediate": 2, "advanced": 3, "expert": 4}
        return levels.get(level.lower(), 2)
    
    def _extract_json_from_response(self, response_text: str) -> Dict:
        """Extract JSON from LLM response (handles markdown code blocks)."""
        try:
            # Try direct parsing first
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Try to extract from markdown code block
            match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
            if match:
                return json.loads(match.group(1))
            
            # Try to find JSON object in text
            match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            
            logger.warning(f"Could not extract JSON from response: {response_text[:200]}")
            return {}
