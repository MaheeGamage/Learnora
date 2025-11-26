"""Test base RDF operations."""

import pytest
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import RDF, RDFS
from pathlib import Path
import tempfile
import shutil
from app.kg.base import KGBase
from app.kg.config import KGConfig


@pytest.fixture
def kg_base():
    """Create a KGBase instance for testing."""
    return KGBase()


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    # Cleanup
    shutil.rmtree(temp_path)


def test_kg_base_namespaces(kg_base):
    """Test that all namespaces are properly initialized."""
    assert str(kg_base.KG) == KGConfig.KG_NAMESPACE
    assert str(kg_base.USERS) == KGConfig.USERS_NAMESPACE
    assert str(kg_base.PATHS) == KGConfig.PATHS_NAMESPACE
    assert kg_base.RDF == RDF
    assert kg_base.RDFS == RDFS


def test_create_graph(kg_base):
    """Test creating a new graph with namespace bindings."""
    g = kg_base.create_graph()
    
    assert isinstance(g, Graph)
    assert len(g) == 0  # Empty graph initially
    
    # Check namespace bindings
    namespaces = dict(g.namespaces())
    assert 'kg' in namespaces
    assert 'users' in namespaces
    assert 'paths' in namespaces
    assert 'rdf' in namespaces


def test_save_and_load_graph(kg_base, temp_dir):
    """Test saving and loading a graph."""
    # Create a simple graph
    g = kg_base.create_graph()
    concept = URIRef(kg_base.KG.Python)
    g.add((concept, RDF.type, kg_base.KG.Concept))
    g.add((concept, RDFS.label, Literal("Python Programming")))
    
    # Save to file
    test_file = temp_dir / "test_graph.ttl"
    kg_base.save_graph(g, test_file)
    
    # Verify file exists
    assert test_file.exists()
    
    # Load the graph back
    loaded_g = kg_base.load_graph(test_file)
    
    # Verify content
    assert loaded_g is not None
    assert len(loaded_g) == 2
    assert (concept, RDF.type, kg_base.KG.Concept) in loaded_g
    assert (concept, RDFS.label, Literal("Python Programming")) in loaded_g


def test_load_nonexistent_graph(kg_base, temp_dir):
    """Test loading a graph that doesn't exist."""
    nonexistent_file = temp_dir / "nonexistent.ttl"
    result = kg_base.load_graph(nonexistent_file)
    
    assert result is None


def test_merge_graphs(kg_base):
    """Test merging multiple graphs."""
    # Create first graph
    g1 = kg_base.create_graph()
    concept1 = URIRef(kg_base.KG.Python)
    g1.add((concept1, RDF.type, kg_base.KG.Concept))
    
    # Create second graph
    g2 = kg_base.create_graph()
    concept2 = URIRef(kg_base.KG.Java)
    g2.add((concept2, RDF.type, kg_base.KG.Concept))
    
    # Merge graphs
    merged = kg_base.merge_graphs(g1, g2)
    
    # Verify merged graph contains both
    assert len(merged) == 2
    assert (concept1, RDF.type, kg_base.KG.Concept) in merged
    assert (concept2, RDF.type, kg_base.KG.Concept) in merged


def test_merge_with_none_graph(kg_base):
    """Test merging graphs when one is None."""
    g1 = kg_base.create_graph()
    concept1 = URIRef(kg_base.KG.Python)
    g1.add((concept1, RDF.type, kg_base.KG.Concept))
    
    # Merge with None
    merged = kg_base.merge_graphs(g1, None)
    
    # Should still have the valid graph's content
    assert len(merged) == 1
    assert (concept1, RDF.type, kg_base.KG.Concept) in merged


def test_save_creates_parent_directory(kg_base, temp_dir):
    """Test that saving creates parent directories if they don't exist."""
    nested_path = temp_dir / "level1" / "level2" / "test.ttl"
    
    g = kg_base.create_graph()
    g.add((URIRef(kg_base.KG.Test), RDF.type, kg_base.KG.Concept))
    
    # This should create the nested directories
    kg_base.save_graph(g, nested_path)
    
    assert nested_path.exists()
    assert nested_path.parent.exists()
