"""Helper class for working with Concept ontology."""

from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDF, RDFS
from app.kg.base import KGBase


class ConceptOntology(KGBase):
    """Helper class for creating and querying concept instances."""
    
    def add_concept(
        self,
        graph: Graph,
        concept_id: str,
        label: str,
        description: str = None
    ) -> URIRef:
        """
        Add a concept to the graph.
        
        Args:
            graph: The RDF graph to add to
            concept_id: Unique identifier for the concept (e.g., "Python", "NeuralNetworks")
            label: Human-readable label
            description: Detailed description
            
        Returns:
            URIRef of the created concept
        """
        concept = URIRef(self.ONT[concept_id])
        
        # Add type
        graph.add((concept, RDF.type, self.ONT.Concept))
        
        # Add label
        graph.add((concept, self.ONT.label, Literal(label)))
        
        # Add optional properties
        if description:
            graph.add((concept, self.ONT.description, Literal(description)))
        
        return concept
    
    def add_prerequisite(self, graph: Graph, concept: URIRef, prerequisite: URIRef) -> None:
        """
        Add a prerequisite relationship between concepts.
        Points backward: concept hasPrerequisite prerequisite
        Example: ArtificialIntelligence hasPrerequisite Mathematics
        
        Args:
            graph: The RDF graph to add to
            concept: The advanced concept that has a prerequisite
            prerequisite: The foundational prerequisite concept
        """
        graph.add((concept, self.ONT.hasPrerequisite, prerequisite))
    
    def get_concept_by_id(self, graph: Graph, concept_id: str) -> URIRef:
        """
        Get a concept URI by its ID.
        
        Args:
            graph: The RDF graph to query
            concept_id: The concept identifier
            
        Returns:
            URIRef of the concept
        """
        return URIRef(self.ONT[concept_id])
    
    def get_all_concepts(self, graph: Graph) -> list[URIRef]:
        """
        Get all concepts from the graph.
        
        Args:
            graph: The RDF graph to query
            
        Returns:
            List of concept URIRefs
        """
        query = """
            SELECT ?concept
            WHERE {
                ?concept rdf:type kg:Concept .
            }
        """
        results = graph.query(query, initNs={'rdf': RDF, 'kg': self.ONT})
        return [row.concept for row in results]
    
    def get_prerequisites(self, graph: Graph, concept: URIRef) -> list[URIRef]:
        """
        Get all prerequisites for a concept.
        
        Args:
            graph: The RDF graph to query
            concept: The concept to get prerequisites for
            
        Returns:
            List of prerequisite concept URIRefs
        """
        query = """
            SELECT ?prereq
            WHERE {
                ?concept kg:hasPrerequisite ?prereq .
            }
        """
        results = graph.query(
            query,
            initBindings={'concept': concept},
            initNs={'kg': self.ONT}
        )
        return [row.prereq for row in results]
