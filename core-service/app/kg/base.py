"""Base classes and utilities for Knowledge Graph operations."""

from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, OWL, XSD
from pathlib import Path
from typing import Optional
from app.kg.config import KGConfig


class KGBase:
    """Base class for Knowledge Graph operations with common namespaces."""
    
    def __init__(self):
        """Initialize base namespaces."""
        # Define namespaces
        self.KG = Namespace(KGConfig.KG_NAMESPACE)
        self.USERS = Namespace(KGConfig.USERS_NAMESPACE)
        self.PATHS = Namespace(KGConfig.PATHS_NAMESPACE)
        
        # Standard namespaces
        self.RDF = RDF
        self.RDFS = RDFS
        self.OWL = OWL
        self.XSD = XSD
    
    def create_graph(self) -> Graph:
        """Create a new RDF graph with standard namespace bindings."""
        g = Graph()
        
        # Bind namespaces
        g.bind("kg", self.KG)
        g.bind("users", self.USERS)
        g.bind("paths", self.PATHS)
        g.bind("rdf", self.RDF)
        g.bind("rdfs", self.RDFS)
        g.bind("owl", self.OWL)
        g.bind("xsd", self.XSD)
        
        return g
    
    def load_graph(self, file_path: Path) -> Optional[Graph]:
        """
        Load an RDF graph from a file.
        
        Args:
            file_path: Path to the RDF file
            
        Returns:
            Graph object if file exists, None otherwise
        """
        if not file_path.exists():
            return None
        
        g = self.create_graph()
        g.parse(file_path, format=KGConfig.RDF_FORMAT)
        return g
    
    def save_graph(self, graph: Graph, file_path: Path) -> None:
        """
        Save an RDF graph to a file.
        
        Args:
            graph: RDF graph to save
            file_path: Path where to save the graph
        """
        # Ensure parent directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Serialize graph to file
        graph.serialize(destination=str(file_path), format=KGConfig.RDF_FORMAT)
    
    def merge_graphs(self, *graphs: Graph) -> Graph:
        """
        Merge multiple RDF graphs into one.
        
        Args:
            *graphs: Variable number of Graph objects to merge
            
        Returns:
            A new Graph containing all triples from input graphs
        """
        merged = self.create_graph()
        for g in graphs:
            if g is not None:
                merged += g
        return merged
