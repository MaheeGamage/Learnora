"""Test storage operations for Knowledge Graph."""

import pytest
from rdflib import URIRef, Literal
from rdflib.namespace import RDF, RDFS
from pathlib import Path
from app.kg.storage import KGStorage
from app.kg.config import KGConfig


@pytest.fixture
def storage():
    """Create a KGStorage instance for testing."""
    return KGStorage()


@pytest.fixture(autouse=True)
def cleanup_test_files():
    """Clean up test files after each test."""
    yield
    # Cleanup test user files
    test_user_file = KGConfig.get_user_file_path("test_user_123")
    if test_user_file.exists():
        test_user_file.unlink()
    
    # Cleanup test learning path files
    test_path_file = KGConfig.get_learning_path_file_path("test_thread_123")
    if test_path_file.exists():
        test_path_file.unlink()


# ===== Concepts Tests =====

def test_load_concepts_nonexistent(storage):
    """Test loading concepts when file doesn't exist."""
    # Temporarily move concepts file if it exists
    if KGConfig.CONCEPTS_FILE.exists():
        backup = KGConfig.CONCEPTS_FILE.with_suffix('.ttl.bak')
        KGConfig.CONCEPTS_FILE.rename(backup)
        try:
            g = storage.load_concepts()
            assert len(g) == 0  # Should return empty graph
        finally:
            backup.rename(KGConfig.CONCEPTS_FILE)
    else:
        g = storage.load_concepts()
        assert len(g) == 0


def test_save_and_load_concepts(storage):
    """Test saving and loading concepts."""
    # Create a concepts graph
    g = storage.create_graph()
    concept = URIRef(storage.KG.TestConcept)
    g.add((concept, RDF.type, storage.KG.Concept))
    g.add((concept, RDFS.label, Literal("Test Concept")))
    
    # Save concepts
    storage.save_concepts(g)
    
    # Load concepts back
    loaded_g = storage.load_concepts()
    
    assert len(loaded_g) == 2
    assert (concept, RDF.type, storage.KG.Concept) in loaded_g


# ===== User Knowledge Tests =====

def test_load_user_knowledge_nonexistent(storage):
    """Test loading user knowledge when file doesn't exist."""
    g = storage.load_user_knowledge("nonexistent_user")
    assert len(g) == 0


def test_save_and_load_user_knowledge(storage):
    """Test saving and loading user knowledge."""
    user_id = "test_user_123"
    
    # Create user knowledge graph
    g = storage.create_graph()
    user = URIRef(storage.USERS[user_id])
    concept = URIRef(storage.KG.Python)
    g.add((user, RDF.type, storage.KG.User))
    g.add((user, storage.KG.knows, concept))
    
    # Save user knowledge
    storage.save_user_knowledge(user_id, g)
    
    # Verify file exists
    assert storage.user_knowledge_exists(user_id)
    
    # Load user knowledge back
    loaded_g = storage.load_user_knowledge(user_id)
    
    assert len(loaded_g) == 2
    assert (user, storage.KG.knows, concept) in loaded_g


def test_user_knowledge_exists(storage):
    """Test checking if user knowledge exists."""
    user_id = "test_user_123"
    
    # Should not exist initially
    assert not storage.user_knowledge_exists(user_id)
    
    # Create and save
    g = storage.create_graph()
    user = URIRef(storage.USERS[user_id])
    g.add((user, RDF.type, storage.KG.User))
    storage.save_user_knowledge(user_id, g)
    
    # Should exist now
    assert storage.user_knowledge_exists(user_id)


# ===== Learning Path Tests =====

def test_load_learning_path_nonexistent(storage):
    """Test loading learning path when file doesn't exist."""
    g = storage.load_learning_path("nonexistent_thread")
    assert len(g) == 0


def test_save_and_load_learning_path(storage):
    """Test saving and loading learning path."""
    thread_id = "test_thread_123"
    
    # Create learning path graph
    g = storage.create_graph()
    path = URIRef(storage.PATHS[thread_id])
    concept = URIRef(storage.KG.Python)
    g.add((path, RDF.type, storage.KG.LearningPath))
    g.add((path, storage.KG.includesConcept, concept))
    
    # Save learning path
    storage.save_learning_path(thread_id, g)
    
    # Verify file exists
    assert storage.learning_path_exists(thread_id)
    
    # Load learning path back
    loaded_g = storage.load_learning_path(thread_id)
    
    assert len(loaded_g) == 2
    assert (path, storage.KG.includesConcept, concept) in loaded_g


def test_learning_path_exists(storage):
    """Test checking if learning path exists."""
    thread_id = "test_thread_123"
    
    # Should not exist initially
    assert not storage.learning_path_exists(thread_id)
    
    # Create and save
    g = storage.create_graph()
    path = URIRef(storage.PATHS[thread_id])
    g.add((path, RDF.type, storage.KG.LearningPath))
    storage.save_learning_path(thread_id, g)
    
    # Should exist now
    assert storage.learning_path_exists(thread_id)


# ===== Ontology Tests =====

def test_load_ontology_nonexistent(storage):
    """Test loading ontology when file doesn't exist."""
    g = storage.load_ontology('concept')
    # Should return empty graph if file doesn't exist
    assert isinstance(g, type(storage.create_graph()))


def test_load_ontology_invalid_name(storage):
    """Test loading ontology with invalid name."""
    g = storage.load_ontology('invalid_ontology_name')
    assert len(g) == 0


def test_load_ontology_valid_names(storage):
    """Test that valid ontology names are recognized."""
    # These should not raise errors and return graphs
    g1 = storage.load_ontology('concept')
    g2 = storage.load_ontology('learning_path')
    g3 = storage.load_ontology('user_knowledge')
    
    assert g1 is not None
    assert g2 is not None
    assert g3 is not None
