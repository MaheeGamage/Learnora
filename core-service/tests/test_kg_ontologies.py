"""Test ontology helper classes."""

import pytest
from rdflib import URIRef, Literal
from rdflib.namespace import RDF
from app.kg.ontologies.concept import ConceptOntology
from app.kg.ontologies.learning_path import LearningPathOntology
from app.kg.ontologies.user_knowledge import UserKnowledgeOntology


@pytest.fixture
def concept_ontology():
    """Create ConceptOntology instance."""
    return ConceptOntology()


@pytest.fixture
def learning_path_ontology():
    """Create LearningPathOntology instance."""
    return LearningPathOntology()


@pytest.fixture
def user_knowledge_ontology():
    """Create UserKnowledgeOntology instance."""
    return UserKnowledgeOntology()


# ===== Concept Ontology Tests =====

def test_add_concept(concept_ontology):
    """Test adding a concept to a graph."""
    g = concept_ontology.create_graph()
    
    concept = concept_ontology.add_concept(
        g,
        concept_id="Python",
        label="Python Programming",
        description="A high-level programming language"
    )
    
    # Verify concept was added
    assert (concept, RDF.type, concept_ontology.KG.Concept) in g
    assert (concept, concept_ontology.KG.label, Literal("Python Programming")) in g
    assert (concept, concept_ontology.KG.description, Literal("A high-level programming language")) in g


def test_add_prerequisite(concept_ontology):
    """Test adding prerequisite relationships."""
    g = concept_ontology.create_graph()
    
    python = concept_ontology.add_concept(g, "Python", "Python Programming")
    ml = concept_ontology.add_concept(g, "MachineLearning", "Machine Learning")
    
    # ML hasPrerequisite Python (backward pointing)
    concept_ontology.add_prerequisite(g, ml, python)
    
    # Verify prerequisite relationship
    assert (ml, concept_ontology.KG.hasPrerequisite, python) in g


def test_get_all_concepts(concept_ontology):
    """Test retrieving all concepts."""
    g = concept_ontology.create_graph()
    
    python = concept_ontology.add_concept(g, "Python", "Python")
    java = concept_ontology.add_concept(g, "Java", "Java")
    
    concepts = concept_ontology.get_all_concepts(g)
    
    assert len(concepts) == 2
    assert python in concepts
    assert java in concepts


def test_get_prerequisites(concept_ontology):
    """Test getting prerequisites for a concept."""
    g = concept_ontology.create_graph()
    
    python = concept_ontology.add_concept(g, "Python", "Python")
    math = concept_ontology.add_concept(g, "Math", "Mathematics")
    ml = concept_ontology.add_concept(g, "ML", "Machine Learning")
    
    concept_ontology.add_prerequisite(g, ml, python)
    concept_ontology.add_prerequisite(g, ml, math)
    
    prereqs = concept_ontology.get_prerequisites(g, ml)
    
    assert len(prereqs) == 2
    assert python in prereqs
    assert math in prereqs


# ===== Learning Path Ontology Tests =====

def test_add_learning_path(learning_path_ontology):
    """Test adding a learning path."""
    g = learning_path_ontology.create_graph()
    
    path = learning_path_ontology.add_learning_path(
        g,
        thread_id="thread_123",
        topic="Python Programming"
    )
    
    # Verify learning path was added
    assert (path, RDF.type, learning_path_ontology.KG.LearningPath) in g
    assert (path, learning_path_ontology.KG.threadId, Literal("thread_123")) in g
    assert (path, learning_path_ontology.KG.topic, Literal("Python Programming")) in g


def test_add_concept_to_path(learning_path_ontology):
    """Test adding concepts to a learning path."""
    g = learning_path_ontology.create_graph()
    
    path = learning_path_ontology.add_learning_path(g, "thread_123", "ML")
    concept = URIRef(learning_path_ontology.KG.Python)
    
    learning_path_ontology.add_concept_to_path(g, path, concept)
    
    # Verify concept was added to path
    assert (path, learning_path_ontology.KG.includesConcept, concept) in g


def test_get_path_concepts(learning_path_ontology):
    """Test getting all concepts in a learning path."""
    g = learning_path_ontology.create_graph()
    
    path = learning_path_ontology.add_learning_path(g, "thread_123", "ML")
    python = URIRef(learning_path_ontology.KG.Python)
    ml = URIRef(learning_path_ontology.KG.MachineLearning)
    
    learning_path_ontology.add_concept_to_path(g, path, python)
    learning_path_ontology.add_concept_to_path(g, path, ml)
    
    concepts = learning_path_ontology.get_path_concepts(g, path)
    
    assert len(concepts) == 2
    assert python in concepts
    assert ml in concepts


# ===== User Knowledge Ontology Tests =====

def test_add_user(user_knowledge_ontology):
    """Test adding a user."""
    g = user_knowledge_ontology.create_graph()
    
    user = user_knowledge_ontology.add_user(g, "user_123")
    
    # Verify user was added
    assert (user, RDF.type, user_knowledge_ontology.KG.User) in g
    assert (user, user_knowledge_ontology.KG.userId, Literal("user_123")) in g


def test_add_known_concept(user_knowledge_ontology):
    """Test marking a concept as known by user."""
    g = user_knowledge_ontology.create_graph()
    
    user = user_knowledge_ontology.add_user(g, "user_123")
    concept = URIRef(user_knowledge_ontology.KG.Python)
    
    user_knowledge_ontology.add_known_concept(g, user, concept)
    
    # Verify relationship
    assert (user, user_knowledge_ontology.KG.knows, concept) in g


def test_add_learning_concept(user_knowledge_ontology):
    """Test marking a concept as currently learning."""
    g = user_knowledge_ontology.create_graph()
    
    user = user_knowledge_ontology.add_user(g, "user_123")
    concept = URIRef(user_knowledge_ontology.KG.MachineLearning)
    
    user_knowledge_ontology.add_learning_concept(g, user, concept)
    
    # Verify relationship
    assert (user, user_knowledge_ontology.KG.learning, concept) in g


def test_add_user_learning_path(user_knowledge_ontology):
    """Test associating user with learning path."""
    g = user_knowledge_ontology.create_graph()
    
    user = user_knowledge_ontology.add_user(g, "user_123")
    path = URIRef(user_knowledge_ontology.PATHS["thread_123"])
    
    user_knowledge_ontology.add_user_learning_path(g, user, path)
    
    # Verify relationship
    assert (user, user_knowledge_ontology.KG.followsPath, path) in g


def test_get_known_concepts(user_knowledge_ontology):
    """Test getting all known concepts for a user."""
    g = user_knowledge_ontology.create_graph()
    
    user = user_knowledge_ontology.add_user(g, "user_123")
    python = URIRef(user_knowledge_ontology.KG.Python)
    java = URIRef(user_knowledge_ontology.KG.Java)
    
    user_knowledge_ontology.add_known_concept(g, user, python)
    user_knowledge_ontology.add_known_concept(g, user, java)
    
    known = user_knowledge_ontology.get_known_concepts(g, user)
    
    assert len(known) == 2
    assert python in known
    assert java in known


def test_get_learning_concepts(user_knowledge_ontology):
    """Test getting concepts user is currently learning."""
    g = user_knowledge_ontology.create_graph()
    
    user = user_knowledge_ontology.add_user(g, "user_123")
    ml = URIRef(user_knowledge_ontology.KG.MachineLearning)
    
    user_knowledge_ontology.add_learning_concept(g, user, ml)
    
    learning = user_knowledge_ontology.get_learning_concepts(g, user)
    
    assert len(learning) == 1
    assert ml in learning


def test_user_knows_concept(user_knowledge_ontology):
    """Test checking if user knows a concept."""
    g = user_knowledge_ontology.create_graph()
    
    user = user_knowledge_ontology.add_user(g, "user_123")
    python = URIRef(user_knowledge_ontology.KG.Python)
    java = URIRef(user_knowledge_ontology.KG.Java)
    
    user_knowledge_ontology.add_known_concept(g, user, python)
    
    assert user_knowledge_ontology.user_knows_concept(g, user, python) is True
    assert user_knowledge_ontology.user_knows_concept(g, user, java) is False
