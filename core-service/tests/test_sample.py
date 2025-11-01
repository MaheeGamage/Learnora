"""Test suite for learning path knowledge graph operations."""

import pytest
from unittest.mock import Mock, patch
from rdflib import Graph, URIRef

from app.features.learning_path.kg import LearningPathKG


@pytest.fixture
def learning_path_kg():
    """Create a LearningPathKG instance with mocked storage and ontologies."""
    with patch('app.features.learning_path.kg.KGStorage'), \
         patch('app.features.learning_path.kg.LearningPathOntology'), \
         patch('app.features.learning_path.kg.ConceptOntology'), \
         patch('app.features.learning_path.kg.UserKnowledgeOntology'):
        kg = LearningPathKG()
        return kg


@pytest.fixture
def test_path_data():
    """Sample learning path data with prerequisites."""
    return [
        {"concept": "ConceptName1", "prerequisites": []},
        {"concept": "ConceptName2", "prerequisites": ["ConceptName1"]},
        {"concept": "ConceptName3", "prerequisites": ["ConceptName1", "ConceptName2"]}
    ]

# def test2():
#     # Create a Graph
#     g = Graph()

#     # Parse in an RDF file hosted on the Internet
#     g.parse("http://www.w3.org/People/Berners-Lee/card")

#     # Loop through each triple in the graph (subj, pred, obj)
#     for subj, pred, obj in g:
#         # Check if there is at least one triple in the Graph
#         if (subj, pred, obj) not in g:
#             raise Exception("It better be!")

#     # Print the number of "triples" in the Graph
#     print(f"Graph g has {len(g)} statements.")
#     # Prints: Graph g has 86 statements.

#     # Print out the entire Graph in the RDF Turtle format
#     a = g.serialize(format="turtle")
    
#     print(a)

def test_learning_path_json_to_rdf_graph(learning_path_kg, test_path_data):
    """Test converting learning path JSON to RDF graph."""
    # Setup mocks
    mock_graph = Graph()
    learning_path_kg.storage.create_graph = Mock(return_value=mock_graph)
    
    path_uri = URIRef("http://example.com/paths/thread123")
    learning_path_kg.learning_path_ontology.add_learning_path = Mock(return_value=path_uri)
    learning_path_kg.learning_path_ontology.add_concept_to_path = Mock()
    
    concepts_graph = Graph()
    learning_path_kg.storage.load_concepts = Mock(return_value=concepts_graph)
    
    learning_path_kg.concept_ontology.get_concept_by_name = Mock(return_value=None)
    
    # Mock concept creation - return URIs for each concept
    concept_uris = {
        "ConceptName1": URIRef("http://example.com/concepts/ConceptName1"),
        "ConceptName2": URIRef("http://example.com/concepts/ConceptName2"),
        "ConceptName3": URIRef("http://example.com/concepts/ConceptName3")
    }
    learning_path_kg.concept_ontology.add_concept = Mock(
        side_effect=lambda g, name: concept_uris[name]
    )
    learning_path_kg.concept_ontology.add_prerequisite = Mock()
    
    # Execute
    result_graph = learning_path_kg.learning_path_json_to_rdf_graph(
        test_path_data,
        thread_id="thread123",
        topic="Test Topic",
        user_id="user123"
    )
    
    g = Graph()
    g.parse("http://www.w3.org/People/Berners-Lee/card")
    
    a = g.serialize(format="turtle")
    b = result_graph.serialize(format="turtle")
    
    # Verify the result is the expected graph
    assert result_graph == mock_graph
    
    # Verify learning path was created with correct parameters
    learning_path_kg.learning_path_ontology.add_learning_path.assert_called_once_with(
        mock_graph,
        thread_id="thread123",
        topic="Test Topic",
        user_id="user123"
    )
    
    # Verify all 3 concepts were added to the path
    assert learning_path_kg.learning_path_ontology.add_concept_to_path.call_count == 3
    
    # Verify prerequisites were added (ConceptName2 has 1, ConceptName3 has 2)
    assert learning_path_kg.concept_ontology.add_prerequisite.call_count == 3
    
    print("✓ All assertions passed!")
    print("✓ Learning path created: thread123")
    print(f"✓ Concepts added: {list(concept_uris.keys())}")
    print("✓ Prerequisites established: 3 relationships")
