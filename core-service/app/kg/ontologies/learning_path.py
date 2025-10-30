"""Helper class for working with Learning Path ontology."""

from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDF
from datetime import datetime
from app.kg.base import KGBase


class LearningPathOntology(KGBase):
    """Helper class for creating and querying learning path instances."""
    
    def add_learning_path(
        self,
        graph: Graph,
        thread_id: str,
        topic: str,
        user_id: str,
        created_at: datetime = None
    ) -> URIRef:
        """
        Add a learning path to the graph.
        Note: Learning paths are now stored within user graphs.
        
        Args:
            graph: The RDF graph to add to (typically a user's graph)
            thread_id: Unique thread identifier
            topic: The learning topic/goal
            user_id: User ID who owns this learning path
            created_at: Creation timestamp (defaults to now)
            
        Returns:
            URIRef of the created learning path
        """
        path = URIRef(self.PATHS[thread_id])
        user = URIRef(self.USERS[user_id])
        
        # Add type
        graph.add((path, RDF.type, self.KG.LearningPath))
        
        # Add properties
        graph.add((path, self.KG.threadId, Literal(thread_id)))
        graph.add((path, self.KG.topic, Literal(topic)))
        
        if created_at:
            graph.add((path, self.KG.createdAt, Literal(created_at)))
        
        # Link user to learning path
        graph.add((user, self.KG.followsPath, path))
        
        return path
    
    def add_concept_to_path(
        self,
        graph: Graph,
        path: URIRef,
        concept: URIRef
    ) -> None:
        """
        Add a concept to a learning path.
        Order is inferred from prerequisite relationships between concepts.
        
        Args:
            graph: The RDF graph to add to
            path: The learning path URI
            concept: The concept URI to add
        """
        graph.add((path, self.KG.includesConcept, concept))
    
    def get_learning_path_by_thread(self, graph: Graph, thread_id: str) -> URIRef:
        """
        Get a learning path URI by thread ID.
        
        Args:
            graph: The RDF graph to query
            thread_id: The thread identifier
            
        Returns:
            URIRef of the learning path
        """
        return URIRef(self.PATHS[thread_id])
    
    def get_path_concepts(self, graph: Graph, path: URIRef) -> list[URIRef]:
        """
        Get all concepts in a learning path.
        
        Args:
            graph: The RDF graph to query
            path: The learning path URI
            
        Returns:
            List of concept URIRefs
        """
        query = """
            SELECT ?concept
            WHERE {
                ?path kg:includesConcept ?concept .
            }
        """
        results = graph.query(
            query,
            initBindings={'path': path},
            initNs={'kg': self.KG}
        )
        return [row.concept for row in results]
