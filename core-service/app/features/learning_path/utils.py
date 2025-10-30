"""Utility functions for learning path processing."""
import json
import re
import logging
from typing import Optional
from app.features.concept.service import ConceptService

logger = logging.getLogger(__name__)


def extract_json_array_from_message(content: str) -> Optional[list]:
    """
    Extract JSON array from AI message content.
    
    The AI sometimes wraps JSON in markdown code blocks or adds extra text.
    This method tries to extract valid JSON array of concepts.
    
    Args:
        content: The message content
        
    Returns:
        Parsed JSON list or None if parsing fails
    """
    # Try to find JSON array in markdown code blocks
    json_match = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', content, re.DOTALL)
    if json_match:
        json_str = json_match.group(1)
    else:
        # Try to find raw JSON array
        json_match = re.search(r'\[.*\]', content, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
        else:
            logger.warning("No JSON array found in message content")
            return None
    
    try:
        data = json.loads(json_str)
        # Validate it's a list
        if not isinstance(data, list):
            logger.error(f"Extracted JSON is not an array: {type(data)}")
            return None
        return data
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON array: {e}")
        return None


def extract_json_from_message(content: str) -> Optional[dict]:
    """
    Extract JSON object (dict) from AI message content.
    
    Used for backward compatibility with JSON-LD format.
    The AI sometimes wraps JSON in markdown code blocks or adds extra text.
    This method tries to extract valid JSON object.
    
    Args:
        content: The message content
        
    Returns:
        Parsed JSON dict or None if parsing fails
    """
    # Try to find JSON in markdown code blocks
    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
    if json_match:
        json_str = json_match.group(1)
    else:
        # Try to find raw JSON
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
        else:
            logger.warning("No JSON object found in message content")
            return None
    
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON object: {e}")
        return None


def parse_and_store_concepts(
    user_id: str,
    thread_id: str,
    topic: str,
    concepts_data: list,
    concept_service: ConceptService,
    create_learning_path_callback
) -> None:
    """
    Parse JSON array of concepts and store in KG.
    
    Args:
        user_id: User identifier who owns this learning path
        thread_id: The thread identifier
        topic: The learning topic
        concepts_data: List of concept objects from the AI
                      [{"concept": "A", "prerequisites": ["B"]}, ...]
        concept_service: ConceptService instance for adding concepts
        create_learning_path_callback: Callback function to create learning path
    """
    try:
        if not concepts_data:
            logger.warning(f"No concepts found in JSON for thread {thread_id}")
            return
        
        concept_ids = []
        
        # First pass: Create all concepts without prerequisites
        for concept_data in concepts_data:
            concept_name = concept_data.get("concept", "")
            
            if not concept_name:
                logger.warning(f"Skipping concept with missing name: {concept_data}")
                continue
            
            # Convert concept name to ID (e.g., "Data Types" -> "data_types")
            concept_id = concept_name.lower().replace(" ", "_").replace("-", "_")
            
            # Add concept (service handles duplicates)
            concept_service.add_concept(
                concept_id=concept_id,
                label=concept_name,
                description=f"Concept for learning path: {topic}"
            )
            concept_ids.append(concept_id)
        
        # Second pass: Add prerequisites
        for concept_data in concepts_data:
            concept_name = concept_data.get("concept", "")
            prerequisites = concept_data.get("prerequisites", [])
            
            if not concept_name:
                continue
            
            concept_id = concept_name.lower().replace(" ", "_").replace("-", "_")
            
            # Convert prerequisite names to IDs
            prereq_ids = [
                prereq.lower().replace(" ", "_").replace("-", "_")
                for prereq in prerequisites
                if prereq
            ]
            
            # Re-add concept with prerequisites (KG layer handles this)
            if prereq_ids:
                concept_service.add_concept(
                    concept_id=concept_id,
                    label=concept_name,
                    prerequisites=prereq_ids
                )
        
        # Create learning path in KG
        if concept_ids:
            create_learning_path_callback(user_id, thread_id, topic, concept_ids)
            logger.info(f"Stored {len(concept_ids)} concepts in KG for thread {thread_id}")
        
    except Exception as e:
        logger.error(f"Error parsing and storing concepts: {e}", exc_info=True)
