"""Helper class for working with User Knowledge ontology."""

from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDF
from datetime import datetime
from app.kg.base import KGBase


class UserKnowledgeOntology(KGBase):
    """Helper class for creating and querying user knowledge instances."""
    
    def add_user(self, graph: Graph, user_id: str) -> URIRef:
        """
        Add a user to the graph.
        
        Args:
            graph: The RDF graph to add to
            user_id: Unique user identifier
            
        Returns:
            URIRef of the created user
        """
        user = URIRef(self.USERS[user_id])
        
        # Add type
        graph.add((user, RDF.type, self.KG.User))
        graph.add((user, self.KG.userId, Literal(user_id)))
        
        return user
    
    def add_known_concept(
        self,
        graph: Graph,
        user: URIRef,
        concept: URIRef,
        learned_at: datetime = None,
        proficiency: str = None
    ) -> None:
        """
        Mark that a user knows a concept.
        
        Args:
            graph: The RDF graph to add to
            user: The user URI
            concept: The concept URI
            learned_at: When the concept was learned
            proficiency: Proficiency level
        """
        graph.add((user, self.KG.knows, concept))
        
        # Note: For simplicity, learned_at and proficiency are not added here
        # They would require reification or blank nodes for proper modeling
        # Can be added later if needed
    
    def add_learning_concept(self, graph: Graph, user: URIRef, concept: URIRef) -> None:
        """
        Mark that a user is currently learning a concept.
        
        Args:
            graph: The RDF graph to add to
            user: The user URI
            concept: The concept URI
        """
        graph.add((user, self.KG.learning, concept))
    
    def add_user_learning_path(self, graph: Graph, user: URIRef, path: URIRef) -> None:
        """
        Associate a user with a learning path they're following.
        Note: This is typically called automatically when creating a learning path.
        
        Args:
            graph: The RDF graph to add to
            user: The user URI
            path: The learning path URI
        """
        graph.add((user, self.KG.followsPath, path))
    
    def get_user_by_id(self, graph: Graph, user_id: str) -> URIRef:
        """
        Get a user URI by user ID.
        
        Args:
            graph: The RDF graph to query
            user_id: The user identifier
            
        Returns:
            URIRef of the user
        """
        return URIRef(self.USERS[user_id])
    
    def get_known_concepts(self, graph: Graph, user: URIRef) -> list[URIRef]:
        """
        Get all concepts a user knows.
        
        Args:
            graph: The RDF graph to query
            user: The user URI
            
        Returns:
            List of concept URIRefs
        """
        query = """
            SELECT ?concept
            WHERE {
                ?user kg:knows ?concept .
            }
        """
        results = graph.query(
            query,
            initBindings={'user': user},
            initNs={'kg': self.KG}
        )
        return [row.concept for row in results]
    
    def get_learning_concepts(self, graph: Graph, user: URIRef) -> list[URIRef]:
        """
        Get all concepts a user is currently learning.
        
        Args:
            graph: The RDF graph to query
            user: The user URI
            
        Returns:
            List of concept URIRefs
        """
        query = """
            SELECT ?concept
            WHERE {
                ?user kg:learning ?concept .
            }
        """
        results = graph.query(
            query,
            initBindings={'user': user},
            initNs={'kg': self.KG}
        )
        return [row.concept for row in results]
    
    def user_knows_concept(self, graph: Graph, user: URIRef, concept: URIRef) -> bool:
        """
        Check if a user knows a specific concept.
        
        Args:
            graph: The RDF graph to query
            user: The user URI
            concept: The concept URI
            
        Returns:
            True if user knows the concept, False otherwise
        """
        return (user, self.KG.knows, concept) in graph
    
    def get_user_learning_paths(self, graph: Graph, user: URIRef) -> list[URIRef]:
        """
        Get all learning paths a user is following.
        
        Args:
            graph: The RDF graph to query
            user: The user URI
            
        Returns:
            List of learning path URIRefs
        """
        query = """
            SELECT ?path
            WHERE {
                ?user kg:followsPath ?path .
            }
        """
        results = graph.query(
            query,
            initBindings={'user': user},
            initNs={'kg': self.KG}
        )
        return [row.path for row in results]
    
    def ensure_user_exists(self, graph: Graph, user_id: str) -> URIRef:
        """
        Ensure a user exists in the graph, creating if necessary.
        
        Args:
            graph: The RDF graph
            user_id: The user identifier
            
        Returns:
            URIRef of the user
        """
        user = URIRef(self.USERS[user_id])
        
        # Check if user already exists
        if (user, RDF.type, self.KG.User) not in graph:
            # Create user if doesn't exist
            graph.add((user, RDF.type, self.KG.User))
            graph.add((user, self.KG.userId, Literal(user_id)))
        
        return user
