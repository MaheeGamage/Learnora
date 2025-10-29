"""Test configuration and basic setup for Knowledge Graph."""

import pytest
from pathlib import Path
from app.kg.config import KGConfig


def test_kg_config_paths():
    """Test that all configured paths are correct."""
    # Base paths
    assert KGConfig.BASE_PATH == Path("./data/graph")
    assert KGConfig.ONTOLOGIES_PATH == Path("./data/graph/ontologies")
    assert KGConfig.INSTANCES_PATH == Path("./data/graph/instances")
    
    # Instance paths
    assert KGConfig.CONCEPTS_FILE == Path("./data/graph/instances/concepts.ttl")
    assert KGConfig.LEARNING_PATHS_DIR == Path("./data/graph/instances/learning_paths")
    assert KGConfig.USERS_DIR == Path("./data/graph/instances/users")
    
    # Ontology paths
    assert KGConfig.CONCEPT_ONTOLOGY == Path("./data/graph/ontologies/concept.ttl")
    assert KGConfig.LEARNING_PATH_ONTOLOGY == Path("./data/graph/ontologies/learning_path.ttl")
    assert KGConfig.USER_KNOWLEDGE_ONTOLOGY == Path("./data/graph/ontologies/user_knowledge.ttl")


def test_kg_config_namespaces():
    """Test that namespaces are defined correctly."""
    assert KGConfig.KG_NAMESPACE == "http://learnora.ai/kg#"
    assert KGConfig.USERS_NAMESPACE == "http://learnora.ai/users#"
    assert KGConfig.PATHS_NAMESPACE == "http://learnora.ai/paths#"


def test_kg_config_format():
    """Test RDF format configuration."""
    assert KGConfig.RDF_FORMAT == "turtle"


def test_directories_exist():
    """Test that ensure_directories creates all necessary directories."""
    # These should already exist from the ensure_directories call in config.py
    assert KGConfig.ONTOLOGIES_PATH.exists()
    assert KGConfig.INSTANCES_PATH.exists()
    assert KGConfig.LEARNING_PATHS_DIR.exists()
    assert KGConfig.USERS_DIR.exists()


def test_get_user_file_path():
    """Test user file path generation."""
    user_id = "test123"
    expected_path = Path("./data/graph/instances/users/user_test123.ttl")
    assert KGConfig.get_user_file_path(user_id) == expected_path


def test_get_learning_path_file_path():
    """Test learning path file path generation."""
    thread_id = "abc-123-def"
    expected_path = Path("./data/graph/instances/learning_paths/thread_abc-123-def.ttl")
    assert KGConfig.get_learning_path_file_path(thread_id) == expected_path
