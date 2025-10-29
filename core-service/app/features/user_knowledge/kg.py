"""Knowledge Graph operations for user knowledge."""

from rdflib import URIRef
from app.kg.storage import KGStorage
from app.kg.ontologies import ConceptOntology, LearningPathOntology, UserKnowledgeOntology
import logging

logger = logging.getLogger(__name__)


class UserKnowledgeKG:
    """Knowledge Graph layer for user knowledge operations."""
    
    def __init__(self):
        """Initialize with KG storage and ontology helpers."""
        self.storage = KGStorage()
        self.user_ontology = UserKnowledgeOntology()
        self.concept_ontology = ConceptOntology()
        self.learning_path_ontology = LearningPathOntology()
    
    def mark_known(self, user_id: str, concept_id: str) -> None:
        """
        Mark that a user knows a concept in the KG.
        
        Args:
            user_id: The user identifier
            concept_id: The concept identifier
        """
        # Load user knowledge graph
        user_graph = self.storage.load_user_knowledge(user_id)
        
        # Get or create user
        user = self.user_ontology.get_user_by_id(user_graph, user_id)
        if not self.storage.user_knowledge_exists(user_id):
            user = self.user_ontology.add_user(user_graph, user_id)
        
        # Get concept
        concepts_graph = self.storage.load_concepts()
        concept = self.concept_ontology.get_concept_by_id(concepts_graph, concept_id)
        
        # Add knowledge relationship
        self.user_ontology.add_known_concept(user_graph, user, concept)
        
        # Save user knowledge
        self.storage.save_user_knowledge(user_id, user_graph)
        logger.info(f"Marked concept {concept_id} as known for user {user_id} in KG")
    
    def mark_learning(self, user_id: str, concept_id: str) -> None:
        """
        Mark that a user is currently learning a concept in the KG.
        
        Args:
            user_id: The user identifier
            concept_id: The concept identifier
        """
        # Load user knowledge graph
        user_graph = self.storage.load_user_knowledge(user_id)
        
        # Get or create user
        user = self.user_ontology.get_user_by_id(user_graph, user_id)
        if not self.storage.user_knowledge_exists(user_id):
            user = self.user_ontology.add_user(user_graph, user_id)
        
        # Get concept
        concepts_graph = self.storage.load_concepts()
        concept = self.concept_ontology.get_concept_by_id(concepts_graph, concept_id)
        
        # Add learning relationship
        self.user_ontology.add_learning_concept(user_graph, user, concept)
        
        # Save user knowledge
        self.storage.save_user_knowledge(user_id, user_graph)
        logger.info(f"Marked concept {concept_id} as learning for user {user_id} in KG")
    
    def assign_path(self, user_id: str, thread_id: str) -> None:
        """
        Assign a learning path to a user in the KG.
        
        Args:
            user_id: The user identifier
            thread_id: The learning path thread identifier
        """
        # Load user knowledge graph
        user_graph = self.storage.load_user_knowledge(user_id)
        
        # Get or create user
        user = self.user_ontology.get_user_by_id(user_graph, user_id)
        if not self.storage.user_knowledge_exists(user_id):
            user = self.user_ontology.add_user(user_graph, user_id)
        
        # Get learning path
        path = self.learning_path_ontology.get_learning_path_by_thread(user_graph, thread_id)
        
        # Assign path to user
        self.user_ontology.add_user_learning_path(user_graph, user, path)
        
        # Save user knowledge
        self.storage.save_user_knowledge(user_id, user_graph)
        logger.info(f"Assigned learning path {thread_id} to user {user_id} in KG")
    
    def get_known_concepts(self, user_id: str) -> list[URIRef]:
        """
        Get all concepts a user knows from the KG.
        
        Args:
            user_id: The user identifier
            
        Returns:
            List of concept URIRefs the user knows
        """
        user_graph = self.storage.load_user_knowledge(user_id)
        user = self.user_ontology.get_user_by_id(user_graph, user_id)
        return self.user_ontology.get_known_concepts(user_graph, user)
    
    def get_learning_concepts(self, user_id: str) -> list[URIRef]:
        """
        Get all concepts a user is currently learning from the KG.
        
        Args:
            user_id: The user identifier
            
        Returns:
            List of concept URIRefs the user is learning
        """
        user_graph = self.storage.load_user_knowledge(user_id)
        user = self.user_ontology.get_user_by_id(user_graph, user_id)
        return self.user_ontology.get_learning_concepts(user_graph, user)
    
    def check_knows_concept(self, user_id: str, concept_id: str) -> bool:
        """
        Check if a user knows a specific concept in the KG.
        
        Args:
            user_id: The user identifier
            concept_id: The concept identifier
            
        Returns:
            True if user knows the concept, False otherwise
        """
        user_graph = self.storage.load_user_knowledge(user_id)
        if len(user_graph) == 0:
            return False
        
        user = self.user_ontology.get_user_by_id(user_graph, user_id)
        concepts_graph = self.storage.load_concepts()
        concept = self.concept_ontology.get_concept_by_id(concepts_graph, concept_id)
        
        return self.user_ontology.user_knows_concept(user_graph, user, concept)
