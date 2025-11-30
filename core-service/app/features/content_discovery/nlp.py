"""Natural Language Processing for query understanding."""

from __future__ import annotations

import re
import string
from typing import Any, Dict, List


class NaturalLanguageProcessor:
    """Process and understand natural language queries with NLP capabilities."""
    
    def __init__(self):
        # Synonym mappings for query expansion (domain-agnostic learning terms)
        # Note: Domain-specific synonyms should be provided by users via custom keywords
        self.synonyms = {
            # Generic learning terms (applicable to ANY domain)
            "tutorial": ["tutorial", "guide", "walkthrough", "how-to", "lesson"],
            "course": ["course", "class", "training", "workshop"],
            "beginner": ["beginner", "novice", "starter", "introductory", "basic"],
            "intermediate": ["intermediate", "medium", "moderate"],
            "advanced": ["advanced", "expert", "professional", "master"],
            "learn": ["learn", "study", "master", "understand"],
            "practice": ["practice", "exercise", "drill", "hands-on"],
            "review": ["review", "revision", "recap", "summary"],
        }
        
        # Intent patterns
        self.intent_patterns = {
            "learning": [
                r"\b(learn|learning|study|understand|master)\b",
                r"\b(want to|need to|how to|how do i)\b",
                r"\b(teach me|show me|help me)\b",
            ],
            "tutorial": [
                r"\b(tutorial|guide|walkthrough|how-?to)\b",
                r"\b(step by step|example|demo)\b",
            ],
            "reference": [
                r"\b(reference|documentation|docs|manual|api)\b",
                r"\b(lookup|look up|find|search)\b",
            ],
            "project": [
                r"\b(project|build|create|make|develop)\b",
                r"\b(application|app|program|software)\b",
            ],
        }
        
        # Difficulty patterns
        self.difficulty_patterns = {
            "beginner": [
                r"\b(beginner|novice|starter|new|introduction|intro|basic|fundamentals|getting started)\b",
                r"\b(never|first time|starting out|new to)\b",
            ],
            "intermediate": [
                r"\b(intermediate|medium|moderate|some experience)\b",
            ],
            "advanced": [
                r"\b(advanced|expert|professional|master|in-?depth|complex)\b",
            ],
        }
        
        # Format patterns
        self.format_patterns = {
            "video": [r"\b(video|videos|watch|visual|screencast)\b"],
            "article": [r"\b(article|articles|read|text|blog|post)\b"],
            "course": [r"\b(course|courses|class|training)\b"],
            "tutorial": [r"\b(tutorial|tutorials|guide|walkthrough)\b"],
            "book": [r"\b(book|books|ebook|e-book)\b"],
        }
        
        # Stop words to filter out
        self.stop_words = {
            "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your",
            "yours", "yourself", "yourselves", "he", "him", "his", "himself", "she",
            "her", "hers", "herself", "it", "its", "itself", "they", "them", "their",
            "theirs", "themselves", "what", "which", "who", "whom", "this", "that",
            "these", "those", "am", "is", "are", "was", "were", "be", "been", "being",
            "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an",
            "the", "and", "but", "if", "or", "because", "as", "until", "while", "of",
            "at", "by", "for", "with", "about", "against", "between", "into", "through",
            "during", "before", "after", "above", "below", "to", "from", "up", "down",
            "in", "out", "on", "off", "over", "under", "again", "further", "then",
            "once", "here", "there", "when", "where", "why", "how", "all", "both",
            "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not",
            "only", "own", "same", "so", "than", "too", "very", "can", "will", "just",
            "should", "now",
        }
    
    def expand_query(self, query: str) -> str:
        """Expand query with synonyms and related terms."""
        query_lower = query.lower()
        expanded_terms = set()
        
        # Add original query terms
        for word in query_lower.split():
            if word not in self.stop_words:
                expanded_terms.add(word)
        
        # Add synonyms
        for key, synonyms in self.synonyms.items():
            if key in query_lower or any(syn in query_lower for syn in synonyms):
                expanded_terms.update(synonyms)
        
        # Combine original query with expanded terms
        expanded = query + " " + " ".join(expanded_terms)
        return expanded
    
    def extract_intent(self, query: str) -> Dict[str, Any]:
        """Extract user intent from query."""
        query_lower = query.lower()
        intents = {}
        
        for intent_name, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, query_lower, re.IGNORECASE):
                    score += 1
            if score > 0:
                intents[intent_name] = score
        
        # Get primary intent (highest score)
        primary_intent = max(intents.items(), key=lambda x: x[1])[0] if intents else "general"
        
        return {
            "primary": primary_intent,
            "all_intents": intents,
            "confidence": max(intents.values()) / len(self.intent_patterns) if intents else 0.0
        }
    
    def extract_entities(self, query: str) -> Dict[str, List[str]]:
        """Extract topics, difficulty, and format from query."""
        query_lower = query.lower()
        entities = {
            "topics": [],
            "difficulty": [],
            "formats": [],
        }
        
        # Extract topics using capitalized words and key terms (domain-agnostic)
        # Capitalized words are likely important topics/concepts
        import re
        capitalized_words = re.findall(r'\b[A-Z][a-z]+(?:[A-Z][a-z]+)*\b', query)
        for word in capitalized_words:
            word_lower = word.lower()
            # Skip if it's a learning-level term
            if word_lower not in ["beginner", "intermediate", "advanced"]:
                entities["topics"].append(word_lower)
        
        # Extract difficulty level
        for difficulty, patterns in self.difficulty_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    entities["difficulty"].append(difficulty)
                    break
        
        # Extract preferred format
        for format_type, patterns in self.format_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    entities["formats"].append(format_type)
                    break
        
        return entities
    
    def extract_key_terms(self, query: str) -> List[str]:
        """Extract important terms from query, filtering stop words."""
        query_lower = query.lower()
        # Remove punctuation
        translator = str.maketrans(string.punctuation, ' ' * len(string.punctuation))
        clean_query = query_lower.translate(translator)
        
        # Extract terms, filter stop words
        terms = [
            term for term in clean_query.split()
            if term and term not in self.stop_words and len(term) > 2
        ]
        
        return terms
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """Comprehensive query processing with all NLP features."""
        return {
            "original_query": query,
            "expanded_query": self.expand_query(query),
            "intent": self.extract_intent(query),
            "entities": self.extract_entities(query),
            "key_terms": self.extract_key_terms(query),
        }
