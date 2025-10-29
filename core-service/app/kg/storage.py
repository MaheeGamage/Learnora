"""Storage operations for Knowledge Graph files."""

from pathlib import Path
from typing import Optional
from rdflib import Graph
from app.kg.base import KGBase
from app.kg.config import KGConfig
import logging

logger = logging.getLogger(__name__)


class KGStorage(KGBase):
    """Handles file-based storage operations for Knowledge Graphs."""
    
    def __init__(self):
        """Initialize storage handler."""
        super().__init__()
        KGConfig.ensure_directories()
    
    # ===== Concepts Storage =====
    
    def load_concepts(self) -> Graph:
        """
        Load the concepts graph.
        
        Returns:
            Graph with all concepts, or empty graph if file doesn't exist
        """
        graph = self.load_graph(KGConfig.CONCEPTS_FILE)
        if graph is None:
            logger.info("Concepts file not found, returning empty graph")
            return self.create_graph()
        logger.info(f"Loaded concepts graph with {len(graph)} triples")
        return graph
    
    def save_concepts(self, graph: Graph) -> None:
        """
        Save the concepts graph.
        
        Args:
            graph: Graph containing concept definitions
        """
        self.save_graph(graph, KGConfig.CONCEPTS_FILE)
        logger.info(f"Saved concepts graph with {len(graph)} triples")
    
    # ===== User Knowledge Storage =====
    
    def load_user_knowledge(self, user_id: str) -> Graph:
        """
        Load a user's knowledge graph.
        
        Args:
            user_id: User identifier
            
        Returns:
            Graph with user's knowledge, or empty graph if file doesn't exist
        """
        file_path = KGConfig.get_user_file_path(user_id)
        graph = self.load_graph(file_path)
        if graph is None:
            logger.info(f"User knowledge file not found for user {user_id}, returning empty graph")
            return self.create_graph()
        logger.info(f"Loaded user {user_id} knowledge graph with {len(graph)} triples")
        return graph
    
    def save_user_knowledge(self, user_id: str, graph: Graph) -> None:
        """
        Save a user's knowledge graph.
        
        Args:
            user_id: User identifier
            graph: Graph containing user's knowledge
        """
        file_path = KGConfig.get_user_file_path(user_id)
        self.save_graph(graph, file_path)
        logger.info(f"Saved user {user_id} knowledge graph with {len(graph)} triples")
    
    def user_knowledge_exists(self, user_id: str) -> bool:
        """
        Check if a user's knowledge graph file exists.
        
        Args:
            user_id: User identifier
            
        Returns:
            True if file exists, False otherwise
        """
        return KGConfig.get_user_file_path(user_id).exists()
    
    # ===== Learning Path Storage =====
    
    def load_learning_path(self, thread_id: str) -> Graph:
        """
        Load a learning path graph.
        
        Args:
            thread_id: Learning path thread identifier
            
        Returns:
            Graph with learning path, or empty graph if file doesn't exist
        """
        file_path = KGConfig.get_learning_path_file_path(thread_id)
        graph = self.load_graph(file_path)
        if graph is None:
            logger.info(f"Learning path file not found for thread {thread_id}, returning empty graph")
            return self.create_graph()
        logger.info(f"Loaded learning path {thread_id} graph with {len(graph)} triples")
        return graph
    
    def save_learning_path(self, thread_id: str, graph: Graph) -> None:
        """
        Save a learning path graph.
        
        Args:
            thread_id: Learning path thread identifier
            graph: Graph containing learning path
        """
        file_path = KGConfig.get_learning_path_file_path(thread_id)
        self.save_graph(graph, file_path)
        logger.info(f"Saved learning path {thread_id} graph with {len(graph)} triples")
    
    def learning_path_exists(self, thread_id: str) -> bool:
        """
        Check if a learning path graph file exists.
        
        Args:
            thread_id: Learning path thread identifier
            
        Returns:
            True if file exists, False otherwise
        """
        return KGConfig.get_learning_path_file_path(thread_id).exists()
    
    # ===== Ontology Storage =====
    
    def load_ontology(self, ontology_name: str) -> Graph:
        """
        Load an ontology file.
        
        Args:
            ontology_name: Name of ontology ('concept', 'learning_path', 'user_knowledge')
            
        Returns:
            Graph with ontology, or empty graph if file doesn't exist
        """
        ontology_files = {
            'concept': KGConfig.CONCEPT_ONTOLOGY,
            'learning_path': KGConfig.LEARNING_PATH_ONTOLOGY,
            'user_knowledge': KGConfig.USER_KNOWLEDGE_ONTOLOGY
        }
        
        file_path = ontology_files.get(ontology_name)
        if file_path is None:
            logger.warning(f"Unknown ontology name: {ontology_name}")
            return self.create_graph()
        
        graph = self.load_graph(file_path)
        if graph is None:
            logger.info(f"Ontology file not found for {ontology_name}, returning empty graph")
            return self.create_graph()
        logger.info(f"Loaded {ontology_name} ontology with {len(graph)} triples")
        return graph
