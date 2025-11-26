"""Integration tests for learning path service."""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from rdflib import Graph, URIRef, Literal
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.learning_path.service import LearningPathService
from app.features.learning_path.schemas import LearningPathCreate
from app.features.users.models import User


@pytest.fixture
def mock_user():
    """Create a mock user for testing."""
    user = Mock(spec=User)
    user.id = 1
    user.email = "test@example.com"
    user.first_name = "Test"
    user.last_name = "User"
    return user


@pytest.fixture
def sample_learning_path_json():
    """Sample learning path JSON data with concepts and prerequisites."""
    return [
        {"concept": "Python Basics", "prerequisites": []},
        {"concept": "Data Structures", "prerequisites": ["Python Basics"]},
        {"concept": "Algorithms", "prerequisites": ["Python Basics", "Data Structures"]}
    ]


@pytest.fixture
def learning_path_service():
    """Create a LearningPathService instance for testing."""
    return LearningPathService()


@pytest.fixture
def mock_db():
    """Create a mock AsyncSession for database operations."""
    db = AsyncMock(spec=AsyncSession)
    db.add = Mock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    return db


# ===== Integration Test for parse_and_save_learning_path =====

def test_parse_and_save_learning_path_integration(
    learning_path_service, 
    mock_db, 
    mock_user, 
    sample_learning_path_json
):
    """
    Integration test for parse_and_save_learning_path.
    Tests the entire flow: JSON -> RDF Graph -> Storage -> Database
    """
    topic = "Python Programming"
    
    # Mock the storage.save_user_graph method
    with patch.object(learning_path_service.storage, 'save_user_graph') as mock_save:
        # Mock the crud.create_learning_path to return a mock learning path
        mock_learning_path = Mock()
        mock_learning_path.id = 1
        mock_learning_path.topic = topic
        mock_learning_path.user_id = mock_user.id
        mock_learning_path.graph_uri = f"http://example.com/ont#{topic.replace(' ', '_').lower()}"
        
        with patch('app.features.learning_path.service.crud.create_learning_path', return_value=mock_learning_path):
            # Execute the function
            result = learning_path_service.parse_and_save_learning_path(
                mock_db, 
                sample_learning_path_json, 
                topic, 
                mock_user
            )
            
            # ===== Assertions =====
            
            # 1. Check that storage.save_user_graph was called
            mock_save.assert_called_once()
            
            # 2. Verify it was called with correct user_id
            assert mock_save.call_args[0][0] == str(mock_user.id)
            
            # 3. Get the saved graph
            saved_graph = mock_save.call_args[0][1]
            assert isinstance(saved_graph, Graph)
            
            # 4. Verify the graph contains the learning path
            learning_path_triples = list(saved_graph.triples(
                (None, learning_path_service.kg_base.RDF.type, learning_path_service.kg_base.ONT.LearningPath)
            ))
            assert len(learning_path_triples) == 1, "Should have exactly one LearningPath"
            
            # 5. Verify concepts were added to the graph
            concept_triples = list(saved_graph.triples(
                (None, learning_path_service.kg_base.RDF.type, learning_path_service.kg_base.ONT.Concept)
            ))
            assert len(concept_triples) == len(sample_learning_path_json), \
                f"Expected {len(sample_learning_path_json)} concepts, found {len(concept_triples)}"
            
            # 6. Verify user was added to the graph
            user_triples = list(saved_graph.triples(
                (None, learning_path_service.kg_base.RDF.type, learning_path_service.kg_base.ONT.User)
            ))
            assert len(user_triples) == 1, "Should have exactly one User"
            
            # 7. Verify user follows the learning path
            follows_triples = list(saved_graph.triples(
                (None, learning_path_service.kg_base.ONT.followsPath, None)
            ))
            assert len(follows_triples) == 1, "User should follow the learning path"
            
            # 8. Verify prerequisites are correctly linked
            prereq_triples = list(saved_graph.triples(
                (None, learning_path_service.kg_base.ONT.hasPrerequisite, None)
            ))
            expected_prereqs = sum(len(item.get("prerequisites", [])) for item in sample_learning_path_json)
            assert len(prereq_triples) == expected_prereqs, \
                f"Expected {expected_prereqs} prerequisites, found {len(prereq_triples)}"
            
            # 9. Verify the result is the created learning path
            # assert result == mock_learning_path
            # assert result.id == 1
            # assert result.topic == topic
            # assert result.user_id == mock_user.id
            
            print("✅ Integration test passed!")
            print(f"   - Learning path created: {result.topic}")
            print(f"   - Graph contains {len(concept_triples)} concepts")
            print(f"   - Graph contains {len(prereq_triples)} prerequisite relationships")
            print(f"   - User {mock_user.id} follows the learning path")


def test_parse_and_save_learning_path_with_empty_prerequisites(
    learning_path_service,
    mock_db,
    mock_user
):
    """Test parse_and_save_learning_path with concepts that have no prerequisites."""
    topic = "Simple Topic"
    json_data = [
        {"concept": "Concept1", "prerequisites": []},
        {"concept": "Concept2", "prerequisites": []},
    ]
    
    with patch.object(learning_path_service.storage, 'save_user_graph') as mock_save:
        mock_learning_path = Mock()
        mock_learning_path.id = 2
        mock_learning_path.topic = topic
        
        with patch('app.features.learning_path.service.crud.create_learning_path', return_value=mock_learning_path):
            learning_path_service.parse_and_save_learning_path(
                mock_db,
                json_data,
                topic,
                mock_user
            )
            
            # Get the saved graph
            saved_graph = mock_save.call_args[0][1]
            
            # Verify no prerequisites exist
            prereq_triples = list(saved_graph.triples(
                (None, learning_path_service.kg_base.ONT.hasPrerequisite, None)
            ))
            assert len(prereq_triples) == 0, "Should have no prerequisites"
            
            # Verify concepts exist
            concept_triples = list(saved_graph.triples(
                (None, learning_path_service.kg_base.RDF.type, learning_path_service.kg_base.ONT.Concept)
            ))
            assert len(concept_triples) == 2
            
            print("✅ Test with empty prerequisites passed!")


def test_parse_and_save_learning_path_graph_structure(
    learning_path_service,
    mock_db,
    mock_user
):
    """Test that the RDF graph structure is correct."""
    topic = "Test Topic"
    json_data = [
        {"concept": "A", "prerequisites": []},
        {"concept": "B", "prerequisites": ["A"]},
    ]
    
    with patch.object(learning_path_service.storage, 'save_user_graph') as mock_save:
        mock_learning_path = Mock()
        
        with patch('app.features.learning_path.service.crud.create_learning_path', return_value=mock_learning_path):
            learning_path_service.parse_and_save_learning_path(
                mock_db,
                json_data,
                topic,
                mock_user
            )
            
            saved_graph = mock_save.call_args[0][1]
            
            # Verify concept labels exist
            label_triples = list(saved_graph.triples(
                (None, learning_path_service.kg_base.ONT.label, None)
            ))
            assert len(label_triples) == 2, "Should have labels for both concepts"
            
            # Extract labels
            labels = [str(triple[2]) for triple in label_triples]
            assert "A" in labels
            assert "B" in labels
            
            # Verify learning path has topic
            topic_triples = list(saved_graph.triples(
                (None, learning_path_service.kg_base.ONT.topic, Literal(topic))
            ))
            assert len(topic_triples) == 1, "Learning path should have a topic"
            
            print("✅ Graph structure test passed!")


def test_convert_learning_path_json_to_rdf_graph(
    learning_path_service,
    sample_learning_path_json
):
    """Test the JSON to RDF graph conversion independently."""
    topic = "Test Conversion"
    
    # Execute conversion
    graph, learning_path_uri = learning_path_service.convert_learning_path_json_to_rdf_graph(
        sample_learning_path_json,
        topic
    )
    
    # Verify graph and URI are returned
    assert isinstance(graph, Graph)
    assert isinstance(learning_path_uri, URIRef)
    
    # Verify learning path exists in graph
    assert (learning_path_uri, learning_path_service.kg_base.RDF.type, 
            learning_path_service.kg_base.ONT.LearningPath) in graph
    
    # Verify topic is set
    assert (learning_path_uri, learning_path_service.kg_base.ONT.topic, 
            Literal(topic)) in graph
    
    # Count concepts
    concepts = list(graph.triples((None, learning_path_service.kg_base.RDF.type, 
                                   learning_path_service.kg_base.ONT.Concept)))
    assert len(concepts) == 3
    
    print("✅ JSON to RDF conversion test passed!")
    print(f"   - Graph contains {len(graph)} triples")
    print(f"   - Learning path URI: {learning_path_uri}")


# ===== Simple Test Runner =====

if __name__ == "__main__":
    """Run tests manually for debugging."""
    print("Running integration tests...\n")
    
    # Create fixtures
    service = LearningPathService()
    user = Mock(spec=User)
    user.id = 1
    user.email = "test@example.com"
    
    db = AsyncMock(spec=AsyncSession)
    
    json_data = [
        {"concept": "Python Basics", "prerequisites": []},
        {"concept": "Data Structures", "prerequisites": ["Python Basics"]},
    ]
    
    # Run test
    try:
        test_parse_and_save_learning_path_integration(service, db, user, json_data)
        print("\n✅ All tests passed!")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
    except Exception as e:
        print(f"\n❌ Error: {e}")