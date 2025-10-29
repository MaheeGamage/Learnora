"""Knowledge Graph operations for concepts."""

from rdflib import URIRef
from typing import Optional
from app.kg.storage import KGStorage
from app.kg.ontologies import ConceptOntology
import logging

logger = logging.getLogger(__name__)


class ConceptKG:
    """Knowledge Graph layer for concept operations."""
    
    def __init__(self):
        """Initialize with KG storage and ontology helper."""
        self.storage = KGStorage()
        self.ontology = ConceptOntology()
    
    def create_concept(
        self,
        concept_id: str,
        label: str,
        description: str = None,
        prerequisites: list[str] = None
    ) -> URIRef:
        """
        Create a new concept in the knowledge graph.
        
        Args:
            concept_id: Unique identifier (e.g., "Python", "MachineLearning")
            label: Human-readable name
            description: Optional detailed description
            prerequisites: List of prerequisite concept IDs
            
        Returns:
            URIRef of the created concept
        """
        # Load existing concepts
        concepts_graph = self.storage.load_concepts()
        
        # Check if concept already exists in the graph
        concept_uri = self.ontology.get_concept_by_id(concepts_graph, concept_id)
        concept_exists = (concept_uri, None, None) in concepts_graph
        
        if concept_exists:
            # Concept exists - just add new prerequisites if provided
            if prerequisites:
                for prereq_id in prerequisites:
                    prereq = self.ontology.get_concept_by_id(concepts_graph, prereq_id)
                    self.ontology.add_prerequisite(concepts_graph, concept_uri, prereq)
                self.storage.save_concepts(concepts_graph)
                logger.info(f"Added prerequisites to existing concept: {concept_id}")
            return concept_uri
        
        # Add new concept
        concept = self.ontology.add_concept(
            concepts_graph,
            concept_id=concept_id,
            label=label,
            description=description
        )
        
        # Add prerequisites if provided
        if prerequisites:
            for prereq_id in prerequisites:
                prereq = self.ontology.get_concept_by_id(concepts_graph, prereq_id)
                self.ontology.add_prerequisite(concepts_graph, concept, prereq)
        
        # Save back to storage
        self.storage.save_concepts(concepts_graph)
        logger.info(f"Created concept in KG: {concept_id}")
        
        return concept
    
    def get_concept(self, concept_id: str) -> Optional[URIRef]:
        """
        Get a concept URI by its ID.
        
        Args:
            concept_id: The concept identifier
            
        Returns:
            URIRef of the concept, or None if concepts graph is empty
        """
        concepts_graph = self.storage.load_concepts()
        if len(concepts_graph) == 0:
            return None
        return self.ontology.get_concept_by_id(concepts_graph, concept_id)
    
    def get_all_concepts(self) -> list[URIRef]:
        """
        Get all concepts from the knowledge graph.
        
        Returns:
            List of concept URIRefs
        """
        concepts_graph = self.storage.load_concepts()
        return self.ontology.get_all_concepts(concepts_graph)
    
    def get_concept_prerequisites(self, concept_id: str) -> list[URIRef]:
        """
        Get all prerequisites for a concept.
        
        Args:
            concept_id: The concept identifier
            
        Returns:
            List of prerequisite concept URIRefs
        """
        concepts_graph = self.storage.load_concepts()
        concept = self.ontology.get_concept_by_id(concepts_graph, concept_id)
        return self.ontology.get_prerequisites(concepts_graph, concept)
    
    def concept_exists(self, concept_id: str) -> bool:
        """
        Check if a concept exists in the KG.
        
        Args:
            concept_id: The concept identifier
            
        Returns:
            True if concept exists, False otherwise
        """
        concepts_graph = self.storage.load_concepts()
        if len(concepts_graph) == 0:
            return False
        
        # Check if the concept actually exists in the graph
        concept_uri = self.ontology.get_concept_by_id(concepts_graph, concept_id)
        # Query the graph to see if this URI has any triples
        return (concept_uri, None, None) in concepts_graph
