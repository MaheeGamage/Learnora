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
    
    # ===== User Knowledge Storage =====
    
    def load_user_graph(self, user_id: str) -> Graph:
        """
        Load a user's complete graph (knowledge + learning paths).
        
        Args:
            user_id: User identifier
            
        Returns:
            Graph with user's knowledge and learning paths, or empty graph if file doesn't exist
        """
        file_path = KGConfig.get_user_file_path(user_id)
        graph = self.load_graph(file_path)
        if graph is None:
            logger.info(f"User graph file not found for user {user_id}, returning empty graph")
            return self.create_graph()
        logger.info(f"Loaded user {user_id} graph with {len(graph)} triples")
        return graph
    
    def save_user_graph(self, user_id: str, graph: Graph, replace: bool = False) -> None:
        """
        Save a user's complete graph (knowledge + learning paths).
        
        Args:
            user_id: User identifier
            graph: Graph containing user's knowledge and learning paths
            replace: If True, replace entire file. If False (default), merge with existing.
        """
        file_path = KGConfig.get_user_file_path(user_id)
        
        if replace:
            # Replace mode: just save the new graph
            self.save_graph(graph, file_path)
            logger.info(f"Replaced user {user_id} graph with {len(graph)} triples")
        else:
            # Merge mode: existing behavior
            existing_graph = self.load_graph(file_path)
            if existing_graph is None:
                # File does not exist or failed to load, create new file
                self.save_graph(graph, file_path)
                logger.info(f"Created new user {user_id} graph with {len(graph)} triples")
            else:
                # File exists, update it
                merged_graph = existing_graph + graph
                self.save_graph(merged_graph, file_path)
                logger.info(f"Updated existing user {user_id} graph with {len(merged_graph)} triples")

    def user_graph_exists(self, user_id: str) -> bool:
        """
        Check if a user's graph file exists.
        
        Args:
            user_id: User identifier
            
        Returns:
            True if file exists, False otherwise
        """
        return KGConfig.get_user_file_path(user_id).exists()
    
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
