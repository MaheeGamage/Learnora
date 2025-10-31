"""Test Knowledge Graph feature services."""

import pytest
from pathlib import Path
from app.features.concept.service import ConceptService
from app.features.learning_path.service import LearningPathService
from app.features.users.knowledge.service import UserKnowledgeService
from app.kg.config import KGConfig


@pytest.fixture
def concept_service():
    """Create a ConceptService instance for testing."""
    return ConceptService()


@pytest.fixture
def learning_path_service():
    """Create a LearningPathService instance for testing."""
    return LearningPathService()


@pytest.fixture
def user_knowledge_service():
    """Create a UserKnowledgeService instance for testing."""
    return UserKnowledgeService()


@pytest.fixture(autouse=True)
def cleanup_test_data():
    """Clean up test data after each test."""
    yield
    
    # Cleanup test concepts file
    if KGConfig.CONCEPTS_FILE.exists():
        KGConfig.CONCEPTS_FILE.unlink()
    
    # Cleanup test user files
    test_user_file = KGConfig.get_user_file_path("test_user_123")
    if test_user_file.exists():
        test_user_file.unlink()
    
    # Cleanup test learning path files
    test_path_file = KGConfig.get_learning_path_file_path("test_thread_123")
    if test_path_file.exists():
        test_path_file.unlink()


# ===== Concept Service Tests =====

def test_add_concept(concept_service):
    """Test adding a concept through the service."""
    concept = concept_service.add_concept(
        concept_id="Python",
        label="Python Programming",
        description="A high-level programming language"
    )
    
    assert concept is not None
    assert KGConfig.CONCEPTS_FILE.exists()


def test_add_concept_with_prerequisites(concept_service):
    """Test adding a concept with prerequisites."""
    concept_service.add_concept("Python", "Python Programming")
    concept_service.add_concept("Math", "Mathematics")
    
    concept_service.add_concept(
        concept_id="MachineLearning",
        label="Machine Learning",
        prerequisites=["Python", "Math"]
    )
    
    prereqs = concept_service.get_concept_prerequisites("MachineLearning")
    assert len(prereqs) == 2


def test_get_all_concepts(concept_service):
    """Test retrieving all concepts."""
    concept_service.add_concept("Python", "Python")
    concept_service.add_concept("Java", "Java")
    
    concepts = concept_service.get_all_concepts()
    assert len(concepts) == 2


def test_get_concept_prerequisites(concept_service):
    """Test getting prerequisites for a concept."""
    concept_service.add_concept("Python", "Python")
    concept_service.add_concept("MachineLearning", "ML", prerequisites=["Python"])
    
    prereqs = concept_service.get_concept_prerequisites("MachineLearning")
    assert len(prereqs) == 1


# ===== Learning Path Service Tests =====

def test_create_learning_path(concept_service, learning_path_service):
    """Test creating a learning path."""
    # Add concepts first
    concept_service.add_concept("Python", "Python")
    concept_service.add_concept("MachineLearning", "ML")
    
    # Create learning path
    path = learning_path_service.create_learning_path_kg(
        thread_id="test_thread_123",
        topic="Machine Learning Basics",
        concept_ids=["Python", "MachineLearning"]
    )
    
    assert path is not None
    assert KGConfig.get_learning_path_file_path("test_thread_123").exists()


def test_get_learning_path_concepts(concept_service, learning_path_service):
    """Test getting concepts from a learning path."""
    # Setup
    concept_service.add_concept("Python", "Python")
    concept_service.add_concept("ML", "Machine Learning")
    learning_path_service.create_learning_path_kg(
        "test_thread_123",
        "ML Path",
        ["Python", "ML"]
    )
    
    # Get concepts
    concepts = learning_path_service.get_learning_path_concepts("test_thread_123")
    assert len(concepts) == 2


# ===== User Knowledge Service Tests =====

def test_mark_concept_as_known(concept_service, user_knowledge_service):
    """Test marking a concept as known by user."""
    # Setup
    concept_service.add_concept("Python", "Python")
    
    # Mark as known
    user_knowledge_service.mark_concept_as_known("test_user_123", "Python")
    
    # Verify
    assert user_knowledge_service.user_knows_concept("test_user_123", "Python") is True
    assert KGConfig.get_user_file_path("test_user_123").exists()


def test_mark_concept_as_learning(concept_service, user_knowledge_service):
    """Test marking a concept as currently learning."""
    # Setup
    concept_service.add_concept("MachineLearning", "ML")
    
    # Mark as learning
    user_knowledge_service.mark_concept_as_learning("test_user_123", "MachineLearning")
    
    # Verify
    learning = user_knowledge_service.get_user_learning_concepts("test_user_123")
    assert len(learning) == 1


def test_get_user_known_concepts(concept_service, user_knowledge_service):
    """Test getting all concepts a user knows."""
    # Setup
    concept_service.add_concept("Python", "Python")
    concept_service.add_concept("Java", "Java")
    
    user_knowledge_service.mark_concept_as_known("test_user_123", "Python")
    user_knowledge_service.mark_concept_as_known("test_user_123", "Java")
    
    # Get known concepts
    known = user_knowledge_service.get_user_known_concepts("test_user_123")
    assert len(known) == 2


def test_user_knows_concept_false(concept_service, user_knowledge_service):
    """Test checking if user knows concept when they don't."""
    concept_service.add_concept("Python", "Python")
    
    assert user_knowledge_service.user_knows_concept("test_user_123", "Python") is False


def test_assign_learning_path_to_user(concept_service, learning_path_service, user_knowledge_service):
    """Test assigning a learning path to a user."""
    # Setup
    concept_service.add_concept("Python", "Python")
    learning_path_service.create_learning_path_kg("test_thread_123", "Python Path", ["Python"])
    
    # Assign to user
    user_knowledge_service.assign_learning_path_to_user("test_user_123", "test_thread_123")
    
    # Verify user file was created/updated
    assert KGConfig.get_user_file_path("test_user_123").exists()


# ===== Integration Tests =====

def test_complete_workflow(concept_service, learning_path_service, user_knowledge_service):
    """Test a complete workflow: concepts -> path -> user."""
    # 1. Add concepts with prerequisites
    concept_service.add_concept("Python", "Python Programming")
    concept_service.add_concept("Math", "Mathematics")
    concept_service.add_concept(
        "MachineLearning",
        "Machine Learning",
        prerequisites=["Python", "Math"]
    )
    
    # 2. Create a learning path
    learning_path_service.create_learning_path_kg(
        "test_thread_123",
        "ML Fundamentals",
        ["Python", "Math", "MachineLearning"]
    )
    
    # 3. User already knows Python
    user_knowledge_service.mark_concept_as_known("test_user_123", "Python")
    
    # 4. User is learning Math
    user_knowledge_service.mark_concept_as_learning("test_user_123", "Math")
    
    # 5. Assign path to user
    user_knowledge_service.assign_learning_path_to_user("test_user_123", "test_thread_123")
    
    # Verify everything
    assert user_knowledge_service.user_knows_concept("test_user_123", "Python") is True
    assert user_knowledge_service.user_knows_concept("test_user_123", "MachineLearning") is False
    
    learning = user_knowledge_service.get_user_learning_concepts("test_user_123")
    assert len(learning) == 1
    
    path_concepts = learning_path_service.get_learning_path_concepts("test_thread_123")
    assert len(path_concepts) == 3
    
    ml_prereqs = concept_service.get_concept_prerequisites("MachineLearning")
    assert len(ml_prereqs) == 2
