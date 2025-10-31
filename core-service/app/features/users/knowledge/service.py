"""User Knowledge service - business logic for user knowledge operations."""

from rdflib import URIRef
from app.features.users.knowledge.kg import UserKnowledgeKG
import logging

logger = logging.getLogger(__name__)


class UserKnowledgeService:
    """Service layer for managing user knowledge with business logic."""
    
    def __init__(self):
        """Initialize user knowledge service with KG layer."""
        self.kg = UserKnowledgeKG()
    
    def mark_concept_as_known(self, user_id: str, concept_id: str) -> None:
        """
        Mark that a user knows a concept.
        
        Business logic: Could add validation, notifications, achievements, etc.
        
        Args:
            user_id: The user identifier
            concept_id: The concept identifier
        """
        # Future: Add business logic like checking if user was learning it first,
        # triggering achievement notifications, updating progress tracking, etc.
        
        self.kg.mark_known(user_id, concept_id)
        logger.info(f"User {user_id} now knows concept: {concept_id}")
    
    def mark_concept_as_learning(self, user_id: str, concept_id: str) -> None:
        """
        Mark that a user is currently learning a concept.
        
        Business logic: Could validate prerequisites are met, limit concurrent learning, etc.
        
        Args:
            user_id: The user identifier
            concept_id: The concept identifier
        """
        # Future: Add business logic like checking prerequisites,
        # limiting number of concurrent learning concepts, etc.
        
        self.kg.mark_learning(user_id, concept_id)
        logger.info(f"User {user_id} is learning concept: {concept_id}")
    
    def assign_learning_path_to_user(self, user_id: str, thread_id: str) -> None:
        """
        Assign a learning path to a user.
        
        Business logic: Could check if user already has active paths, send notifications, etc.
        
        Args:
            user_id: The user identifier
            thread_id: The learning path thread identifier
        """
        # Future: Add business logic like checking for existing active paths,
        # sending notifications, updating user dashboard, etc.
        
        self.kg.assign_path(user_id, thread_id)
        logger.info(f"Assigned learning path {thread_id} to user {user_id}")
    
    def get_user_known_concepts(self, user_id: str) -> list[URIRef]:
        """
        Get all concepts a user knows.
        
        Args:
            user_id: The user identifier
            
        Returns:
            List of concept URIRefs the user knows
        """
        return self.kg.get_known_concepts(user_id)
    
    def get_user_learning_concepts(self, user_id: str) -> list[URIRef]:
        """
        Get all concepts a user is currently learning.
        
        Args:
            user_id: The user identifier
            
        Returns:
            List of concept URIRefs the user is learning
        """
        return self.kg.get_learning_concepts(user_id)
    
    def user_knows_concept(self, user_id: str, concept_id: str) -> bool:
        """
        Check if a user knows a specific concept.
        
        Args:
            user_id: The user identifier
            concept_id: The concept identifier
            
        Returns:
            True if user knows the concept, False otherwise
        """
        return self.kg.check_knows_concept(user_id, concept_id)
