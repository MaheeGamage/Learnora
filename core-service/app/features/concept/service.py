"""Concept service - business logic for concept operations."""

from rdflib import URIRef
from typing import Optional
from app.features.concept.kg import ConceptKG
import logging

logger = logging.getLogger(__name__)


class ConceptService:
    """Service layer for managing concepts with business logic."""
    
    def __init__(self):
        """Initialize concept service with KG layer."""
        self.kg = ConceptKG()
    
    def add_concept(
        self,
        concept_id: str,
        label: str,
        description: str = None,
        prerequisites: list[str] = None
    ) -> URIRef:
        """
        Add a new concept.
        
        Business logic: Validates prerequisites exist before adding.
        If concept already exists, adds any new prerequisites.
        
        Args:
            concept_id: Unique identifier (e.g., "Python", "MachineLearning")
            label: Human-readable name
            description: Optional detailed description
            prerequisites: List of prerequisite concept IDs
            
        Returns:
            URIRef of the created concept
        """
        # Business validation: verify all prerequisites exist
        if prerequisites:
            for prereq_id in prerequisites:
                if not self.kg.concept_exists(prereq_id):
                    raise ValueError(f"Prerequisite concept '{prereq_id}' does not exist")
        
        # Delegate to KG layer (handles duplicates)
        concept = self.kg.create_concept(concept_id, label, description, prerequisites)
        logger.info(f"Added concept: {concept_id}")
        return concept
    
    def get_concept(self, concept_id: str) -> Optional[URIRef]:
        """
        Get a concept URI by its ID.
        
        Args:
            concept_id: The concept identifier
            
        Returns:
            URIRef of the concept, or None if not found
        """
        return self.kg.get_concept(concept_id)
    
    def get_all_concepts(self) -> list[URIRef]:
        """
        Get all concepts.
        
        Returns:
            List of concept URIRefs
        """
        return self.kg.get_all_concepts()
    
    def get_concept_prerequisites(self, concept_id: str) -> list[URIRef]:
        """
        Get all prerequisites for a concept.
        
        Args:
            concept_id: The concept identifier
            
        Returns:
            List of prerequisite concept URIRefs
        """
        return self.kg.get_concept_prerequisites(concept_id)
