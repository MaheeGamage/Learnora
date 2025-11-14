"""Utility functions for MCQ generator."""

from typing import List, Dict, Optional


def extract_concept_label(concept: Dict) -> str:
    """
    Extract the label from a JSON-LD concept.
    
    Args:
        concept: Concept dictionary in JSON-LD format
        
    Returns:
        The concept label as a string
    """
    if "http://learnora.ai/ont#label" in concept:
        labels = concept["http://learnora.ai/ont#label"]
        if labels:
            return labels[0].get("@value", "Unknown Concept")
    return "Unknown Concept"


def find_concept_by_id(learning_path: List[Dict], concept_id: str) -> Optional[Dict]:
    """
    Find a concept in the learning path by its ID.
    
    Args:
        learning_path: List of concepts in JSON-LD format
        concept_id: The @id of the concept to find
        
    Returns:
        The concept dictionary if found, None otherwise
    """
    for concept in learning_path:
        if concept.get("@id") == concept_id:
            return concept
    return None


def extract_prerequisites(learning_path: List[Dict], concept_id: str, max_depth: int = 3) -> List[str]:
    """
    Extract prerequisite concept names recursively.
    
    Args:
        learning_path: List of concepts in JSON-LD format
        concept_id: The @id of the concept to extract prerequisites for
        max_depth: Maximum recursion depth to avoid infinite loops
        
    Returns:
        List of prerequisite concept names
    """
    if max_depth == 0:
        return []
    
    concept = find_concept_by_id(learning_path, concept_id)
    if not concept:
        return []
    
    prerequisites = []
    prereq_key = "http://learnora.ai/ont#hasPrerequisite"
    
    if prereq_key in concept:
        for prereq_ref in concept[prereq_key]:
            prereq_id = prereq_ref.get("@id")
            if prereq_id:
                prereq_concept = find_concept_by_id(learning_path, prereq_id)
                if prereq_concept:
                    prereq_label = extract_concept_label(prereq_concept)
                    prerequisites.append(prereq_label)
                    
                    # Recursively get prerequisites of prerequisites
                    nested_prereqs = extract_prerequisites(
                        learning_path, 
                        prereq_id, 
                        max_depth - 1
                    )
                    prerequisites.extend(nested_prereqs)
    
    return prerequisites


def build_learning_path_context(
    learning_path: Optional[List[Dict]], 
    concept_id: Optional[str]
) -> str:
    """
    Build a human-readable learning path context string.
    
    Args:
        learning_path: Optional list of concepts in JSON-LD format
        concept_id: Optional concept ID to extract prerequisites for
        
    Returns:
        Formatted string describing the learning path context
    """
    if not learning_path or not concept_id:
        return "No prerequisite information provided."
    
    # Find the current concept
    concept = find_concept_by_id(learning_path, concept_id)
    if not concept:
        return "Concept not found in learning path."
    
    # Extract immediate prerequisites
    prereq_key = "http://learnora.ai/ont#hasPrerequisite"
    if prereq_key not in concept or not concept[prereq_key]:
        return "No prerequisites for this concept."
    
    # Get prerequisite names
    immediate_prereqs = []
    for prereq_ref in concept[prereq_key]:
        prereq_id = prereq_ref.get("@id")
        if prereq_id:
            prereq_concept = find_concept_by_id(learning_path, prereq_id)
            if prereq_concept:
                immediate_prereqs.append(extract_concept_label(prereq_concept))
    
    if not immediate_prereqs:
        return "No prerequisites for this concept."
    
    # Format the context
    if len(immediate_prereqs) == 1:
        context = f"This concept builds upon: {immediate_prereqs[0]}"
    else:
        prereq_list = ", ".join(immediate_prereqs[:-1]) + f" and {immediate_prereqs[-1]}"
        context = f"This concept builds upon: {prereq_list}"
    
    # Get all prerequisites (including nested)
    all_prereqs = extract_prerequisites(learning_path, concept_id)
    if all_prereqs:
        # Remove duplicates while preserving order
        unique_prereqs = []
        seen = set()
        for prereq in all_prereqs:
            if prereq not in seen:
                unique_prereqs.append(prereq)
                seen.add(prereq)
        
        if len(unique_prereqs) > len(immediate_prereqs):
            context += f"\n\nFoundational concepts in the learning path: {' → '.join(unique_prereqs[:5])}"
            if len(unique_prereqs) > 5:
                context += f" (and {len(unique_prereqs) - 5} more)"
    
    return context


def extract_learning_path_topic(learning_path: Optional[List[Dict]]) -> Optional[str]:
    """
    Extract the topic/goal from a learning path.
    
    Args:
        learning_path: Optional list of concepts in JSON-LD format
        
    Returns:
        The learning path topic if found
    """
    if not learning_path:
        return None
    
    # Look for a LearningPath object with a topic
    for item in learning_path:
        if "http://learnora.ai/ont#LearningPath" in item.get("@type", []):
            topic_key = "http://learnora.ai/ont#topic"
            if topic_key in item:
                topics = item[topic_key]
                if topics:
                    return topics[0].get("@value")
    
    return None
