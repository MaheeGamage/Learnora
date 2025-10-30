"""Knowledge Graph operations for learning paths."""

from rdflib import Graph as RDFGraph, URIRef
from typing import Optional
from app.kg.storage import KGStorage
from app.kg.ontologies import ConceptOntology, LearningPathOntology
import logging

logger = logging.getLogger(__name__)

class LearningPathKG:
    """Knowledge Graph layer for learning path operations."""
    
    def __init__(self):
        """Initialize with KG storage and ontology helpers."""
        self.storage = KGStorage()
        self.learning_path_ontology = LearningPathOntology()
        self.concept_ontology = ConceptOntology()
    
    def create_path(
        self,
        thread_id: str,
        topic: str,
        concept_ids: list[str]
    ) -> URIRef:
        """
        Create a new learning path in the Knowledge Graph.
        
        Args:
            thread_id: Unique thread identifier
            topic: The learning topic/goal
            concept_ids: List of concept IDs to include in the path
            
        Returns:
            URIRef of the created learning path
        """
        # Create new graph for this learning path
        path_graph = self.storage.create_graph()
        
        # Add the learning path
        path = self.learning_path_ontology.add_learning_path(
            path_graph,
            thread_id=thread_id,
            topic=topic
        )
        
        # Add concepts to the path
        concepts_graph = self.storage.load_concepts()
        for concept_id in concept_ids:
            concept = self.concept_ontology.get_concept_by_id(concepts_graph, concept_id)
            self.learning_path_ontology.add_concept_to_path(path_graph, path, concept)
        
        # Save the learning path
        self.storage.save_learning_path(thread_id, path_graph)
        logger.info(f"Created learning path in KG: {thread_id} with {len(concept_ids)} concepts")
        
        return path
    
    def get_path(self, thread_id: str) -> Optional[RDFGraph]:
        """
        Get a learning path graph from KG.
        
        Args:
            thread_id: The thread identifier
            
        Returns:
            RDFGraph containing the learning path, or empty graph if not found
        """
        return self.storage.load_learning_path(thread_id)
    
    def get_path_concepts(self, thread_id: str) -> list[URIRef]:
        """
        Get all concepts in a learning path from KG.
        
        Args:
            thread_id: The thread identifier
            
        Returns:
            List of concept URIRefs in the learning path
        """
        path_graph = self.storage.load_learning_path(thread_id)
        path = self.learning_path_ontology.get_learning_path_by_thread(path_graph, thread_id)
        return self.learning_path_ontology.get_path_concepts(path_graph, path)
    
    def path_exists(self, thread_id: str) -> bool:
        """
        Check if a learning path exists in the KG.
        
        Args:
            thread_id: The thread identifier
            
        Returns:
            True if path exists, False otherwise
        """
        return self.storage.learning_path_exists(thread_id)
