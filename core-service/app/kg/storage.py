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
    
    def save_user_graph(self, user_id: str, graph: Graph) -> None:
        """
        Save a user's complete graph (knowledge + learning paths).
        
        Args:
            user_id: User identifier
            graph: Graph containing user's knowledge and learning paths
        """
        file_path = KGConfig.get_user_file_path(user_id)
        self.save_graph(graph, file_path)
        logger.info(f"Saved user {user_id} graph with {len(graph)} triples")
    
    def user_graph_exists(self, user_id: str) -> bool:
        """
        Check if a user's graph file exists.
        
        Args:
            user_id: User identifier
            
        Returns:
            True if file exists, False otherwise
        """
        return KGConfig.get_user_file_path(user_id).exists()
    
    # Legacy method names for backward compatibility
    def load_user_knowledge(self, user_id: str) -> Graph:
        """Load user graph (alias for load_user_graph)."""
        return self.load_user_graph(user_id)
    
    def save_user_knowledge(self, user_id: str, graph: Graph) -> None:
        """Save user graph (alias for save_user_graph)."""
        self.save_user_graph(user_id, graph)
    
    def user_knowledge_exists(self, user_id: str) -> bool:
        """Check if user graph exists (alias for user_graph_exists)."""
        return self.user_graph_exists(user_id)
    
    # ===== Learning Path Storage (within user graph) =====
    
    def load_learning_path(self, user_id: str, thread_id: str) -> Graph:
        """
        Load a specific learning path from a user's graph.
        
        Args:
            user_id: User identifier who owns the learning path
            thread_id: Learning path thread identifier
            
        Returns:
            Graph with only the specific learning path triples
        """
        user_graph = self.load_user_graph(user_id)
        
        # Filter to only triples related to this learning path
        from rdflib import URIRef, Namespace
        paths_ns = Namespace(KGConfig.PATHS_NAMESPACE)
        path_uri = paths_ns[thread_id]
        
        # Create a new graph with only this learning path's triples
        path_graph = self.create_graph()
        
        # Get all triples where the path is subject
        for s, p, o in user_graph.triples((path_uri, None, None)):
            path_graph.add((s, p, o))
        
        # Get all triples where the path is object (e.g., user followsPath)
        for s, p, o in user_graph.triples((None, None, path_uri)):
            path_graph.add((s, p, o))
        
        logger.info(f"Loaded learning path {thread_id} for user {user_id} with {len(path_graph)} triples")
        return path_graph
    
    def save_learning_path(self, user_id: str, thread_id: str, path_graph: Graph) -> None:
        """
        Save or update a specific learning path within a user's graph.
        This merges the path_graph into the user's existing graph.
        
        Args:
            user_id: User identifier who owns the learning path
            thread_id: Learning path thread identifier
            path_graph: Graph containing the learning path data
        """
        # Load existing user graph
        user_graph = self.load_user_graph(user_id)
        
        # Remove existing triples for this learning path
        from rdflib import URIRef, Namespace
        paths_ns = Namespace(KGConfig.PATHS_NAMESPACE)
        path_uri = paths_ns[thread_id]
        
        # Remove all triples where the path is subject
        triples_to_remove = list(user_graph.triples((path_uri, None, None)))
        for triple in triples_to_remove:
            user_graph.remove(triple)
        
        # Merge the new path graph
        for s, p, o in path_graph:
            user_graph.add((s, p, o))
        
        # Save the updated user graph
        self.save_user_graph(user_id, user_graph)
        logger.info(f"Saved learning path {thread_id} for user {user_id} (total graph: {len(user_graph)} triples)")
    
    def learning_path_exists(self, user_id: str, thread_id: str) -> bool:
        """
        Check if a specific learning path exists in a user's graph.
        
        Args:
            user_id: User identifier
            thread_id: Learning path thread identifier
            
        Returns:
            True if learning path exists in user's graph, False otherwise
        """
        if not self.user_graph_exists(user_id):
            return False
        
        user_graph = self.load_user_graph(user_id)
        from rdflib import URIRef, Namespace
        paths_ns = Namespace(KGConfig.PATHS_NAMESPACE)
        path_uri = paths_ns[thread_id]
        
        # Check if any triples exist for this path
        for _ in user_graph.triples((path_uri, None, None)):
            return True
        return False
    
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
