"""
Unit tests for Learning Path Service functions.

Tests the core functionality of:
- convert_learning_path_json_to_rdf_graph
- parse_and_save_learning_path
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, AsyncMock
from rdflib import URIRef, Literal, Graph
from rdflib.namespace import RDF
from typing import List, Dict, Any

from app.features.learning_path.service import LearningPathService
from app.features.learning_path.schemas import LearningPathCreate
from app.features.users.models import User
from app.kg.config import KGConfig


@pytest.fixture
def learning_path_service():
    """Create a LearningPathService instance for testing."""
    return LearningPathService()


@pytest.fixture
def mock_user():
    """Create a mock User object for testing."""
    user = Mock(spec=User)
    user.id = 1
    user.email = "test@example.com"
    user.first_name = "Test"
    user.last_name = "User"
    return user


@pytest.fixture
def sample_learning_path_json():
    """Sample JSON data for learning path with concepts and prerequisites."""
    return [
        {
            "concept": "Python Programming Fundamentals",
            "prerequisites": []
        },
        {
            "concept": "NumPy and Pandas",
            "prerequisites": ["Python Programming Fundamentals"]
        },
        {
            "concept": "Introduction to Machine Learning",
            "prerequisites": ["Python Programming Fundamentals"]
        },
        {
            "concept": "Data Preprocessing and Feature Engineering",
            "prerequisites": ["NumPy and Pandas"]
        }
    ]


@pytest.fixture
def simple_learning_path_json():
    """Simple JSON data with single concept (no prerequisites)."""
    return [
        {
            "concept": "Linear Algebra for ML",
            "prerequisites": []
        }
    ]


@pytest.fixture
def complex_learning_path_json():
    """Complex JSON data with special characters in concept names."""
    return [
        {
            "concept": "Deep Learning Frameworks (TensorFlow/PyTorch)",
            "prerequisites": []
        },
        {
            "concept": "Convolutional Neural Networks (CNNs)",
            "prerequisites": ["Deep Learning Frameworks (TensorFlow/PyTorch)"]
        },
        {
            "concept": "Natural Language Processing (NLP) Fundamentals",
            "prerequisites": ["Convolutional Neural Networks (CNNs)"]
        }
    ]


@pytest.fixture(autouse=True)
def cleanup_test_files():
    """Clean up test files after each test."""
    yield
    # Cleanup test user files
    test_user_file = KGConfig.get_user_file_path("1")
    if test_user_file.exists():
        test_user_file.unlink()


# ===== Tests for convert_learning_path_json_to_rdf_graph =====

class TestConvertLearningPathJsonToRdfGraph:
    """Tests for convert_learning_path_json_to_rdf_graph function."""

    def test_basic_conversion(self, learning_path_service, sample_learning_path_json):
        """Test basic conversion of JSON to RDF graph."""
        topic = "machine learning"
        
        graph, learning_path_uri = learning_path_service.convert_learning_path_json_to_rdf_graph(
            sample_learning_path_json, topic
        )
        
        # Verify return types
        assert isinstance(graph, Graph)
        assert isinstance(learning_path_uri, URIRef)
        
        # Verify graph is not empty
        assert len(graph) > 0

    def test_learning_path_creation(self, learning_path_service, sample_learning_path_json):
        """Test that learning path entity is created with correct properties."""
        topic = "machine learning"
        
        graph, learning_path_uri = learning_path_service.convert_learning_path_json_to_rdf_graph(
            sample_learning_path_json, topic
        )
        
        # Verify learning path is of type LearningPath
        assert (learning_path_uri, RDF.type, learning_path_service.kg_base.ONT.LearningPath) in graph
        
        # Verify learning path has topic property
        assert (learning_path_uri, learning_path_service.kg_base.ONT.topic, Literal(topic)) in graph

    def test_concept_creation(self, learning_path_service, sample_learning_path_json):
        """Test that concepts are created with correct properties."""
        topic = "machine learning"
        
        graph, _ = learning_path_service.convert_learning_path_json_to_rdf_graph(
            sample_learning_path_json, topic
        )
        
        # Check each concept from JSON
        for item in sample_learning_path_json:
            concept_name = item["concept"]
            
            # Verify concept is of type Concept
            concept_type_triples = list(graph.triples((None, RDF.type, learning_path_service.kg_base.ONT.Concept)))
            assert len(concept_type_triples) == len(sample_learning_path_json)
            
            # Verify concept has label with original name
            labels = list(graph.triples((None, learning_path_service.kg_base.ONT.label, Literal(concept_name))))
            assert len(labels) > 0

    def test_concept_inclusion_in_path(self, learning_path_service, sample_learning_path_json):
        """Test that all concepts are included in the learning path."""
        topic = "machine learning"
        
        graph, learning_path_uri = learning_path_service.convert_learning_path_json_to_rdf_graph(
            sample_learning_path_json, topic
        )
        
        # Count includesConcept relationships
        includes_triples = list(graph.triples(
            (learning_path_uri, learning_path_service.kg_base.ONT.includesConcept, None)
        ))
        
        assert len(includes_triples) == len(sample_learning_path_json)

    def test_prerequisites_creation(self, learning_path_service, sample_learning_path_json):
        """Test that prerequisites are correctly linked."""
        topic = "machine learning"
        
        graph, _ = learning_path_service.convert_learning_path_json_to_rdf_graph(
            sample_learning_path_json, topic
        )
        
        # Count total prerequisite relationships
        prereq_triples = list(graph.triples(
            (None, learning_path_service.kg_base.ONT.hasPrerequisite, None)
        ))
        
        # Calculate expected number of prerequisites from JSON
        expected_prereqs = sum(len(item.get("prerequisites", [])) for item in sample_learning_path_json)
        assert len(prereq_triples) == expected_prereqs

    def test_single_concept_no_prerequisites(self, learning_path_service, simple_learning_path_json):
        """Test conversion with single concept and no prerequisites."""
        topic = "mathematics"
        
        graph, _ = learning_path_service.convert_learning_path_json_to_rdf_graph(
            simple_learning_path_json, topic
        )
        
        # Verify graph has correct number of triples
        # Should have: 1 LearningPath type, 1 topic, 1 Concept type, 1 label, 1 includesConcept
        assert len(graph) >= 5
        
        # Verify no prerequisites
        prereq_triples = list(graph.triples(
            (None, learning_path_service.kg_base.ONT.hasPrerequisite, None)
        ))
        assert len(prereq_triples) == 0

    def test_special_characters_in_concept_names(self, learning_path_service, complex_learning_path_json):
        """Test that special characters in concept names are properly normalized."""
        topic = "deep learning"
        
        graph, _ = learning_path_service.convert_learning_path_json_to_rdf_graph(
            complex_learning_path_json, topic
        )
        
        # Verify graph is created successfully
        assert len(graph) > 0
        
        # Verify concepts are created (should handle parentheses and slashes)
        concept_type_triples = list(graph.triples((None, RDF.type, learning_path_service.kg_base.ONT.Concept)))
        assert len(concept_type_triples) == len(complex_learning_path_json)
        
        # Verify labels preserve original names with special characters
        for item in complex_learning_path_json:
            concept_name = item["concept"]
            labels = list(graph.triples((None, learning_path_service.kg_base.ONT.label, Literal(concept_name))))
            assert len(labels) > 0, f"Label not found for: {concept_name}"

    def test_empty_json_data(self, learning_path_service):
        """Test conversion with empty JSON data."""
        topic = "test topic"
        empty_json = []
        
        _, learning_path_uri = learning_path_service.convert_learning_path_json_to_rdf_graph(
            empty_json, topic
        )
        
        # Get the graph again to check it
        graph, _ = learning_path_service.convert_learning_path_json_to_rdf_graph(
            empty_json, topic
        )
        
        # Should still create learning path entity
        assert (learning_path_uri, RDF.type, learning_path_service.kg_base.ONT.LearningPath) in graph
        assert (learning_path_uri, learning_path_service.kg_base.ONT.topic, Literal(topic)) in graph
        
        # Should have no concepts
        concept_triples = list(graph.triples((None, RDF.type, learning_path_service.kg_base.ONT.Concept)))
        assert len(concept_triples) == 0

    def test_topic_normalization(self, learning_path_service, sample_learning_path_json):
        """Test that topic is normalized correctly in URI."""
        topic = "Machine Learning Basics"
        
        _, learning_path_uri = learning_path_service.convert_learning_path_json_to_rdf_graph(
            sample_learning_path_json, topic
        )
        
        # URI should have normalized topic (lowercase, underscores)
        expected_normalized = "machine_learning_basics"
        assert expected_normalized in str(learning_path_uri)

    def test_multiple_prerequisites(self, learning_path_service):
        """Test concept with multiple prerequisites."""
        json_data = [
            {"concept": "Concept A", "prerequisites": []},
            {"concept": "Concept B", "prerequisites": []},
            {"concept": "Concept C", "prerequisites": ["Concept A", "Concept B"]}
        ]
        topic = "test"
        
        graph, _ = learning_path_service.convert_learning_path_json_to_rdf_graph(
            json_data, topic
        )
        
        # Find Concept C URI
        concept_c_label_triples = list(graph.triples(
            (None, learning_path_service.kg_base.ONT.label, Literal("Concept C"))
        ))
        assert len(concept_c_label_triples) == 1
        concept_c_uri = concept_c_label_triples[0][0]
        
        # Count prerequisites for Concept C
        prereqs = list(graph.triples(
            (concept_c_uri, learning_path_service.kg_base.ONT.hasPrerequisite, None)
        ))
        assert len(prereqs) == 2

    def test_graph_namespaces(self, learning_path_service, sample_learning_path_json):
        """Test that graph has correct namespace bindings."""
        topic = "test"
        
        graph, _ = learning_path_service.convert_learning_path_json_to_rdf_graph(
            sample_learning_path_json, topic
        )
        
        # Check namespace bindings
        namespaces = dict(graph.namespaces())
        assert 'ont' in namespaces
        assert 'rdf' in namespaces
        assert 'rdfs' in namespaces


# ===== Tests for parse_and_save_learning_path =====

class TestParseAndSaveLearningPath:
    """Tests for parse_and_save_learning_path function."""

    @patch('app.features.learning_path.service.crud.create_learning_path')
    def test_basic_save_functionality(self, mock_create_learning_path, learning_path_service, 
                                     mock_user, sample_learning_path_json):
        """Test basic functionality of parsing and saving learning path."""
        # Setup mock
        mock_db = AsyncMock()
        topic = "machine learning"
        mock_db_learning_path = Mock()
        mock_db_learning_path.id = 1
        mock_db_learning_path.topic = topic
        mock_db_learning_path.user_id = mock_user.id
        mock_create_learning_path.return_value = mock_db_learning_path
        
        # Execute
        with patch.object(learning_path_service.storage, 'save_user_graph') as mock_save:
            result = learning_path_service.parse_and_save_learning_path(
                mock_db, sample_learning_path_json, topic, mock_user
            )
        
        # Verify storage was called
        mock_save.assert_called_once()
        assert mock_save.call_args[0][0] == str(mock_user.id)
        
        # Verify CRUD was called
        mock_create_learning_path.assert_called_once()
        
        # Verify result
        assert result == mock_db_learning_path

    @patch('app.features.learning_path.service.crud.create_learning_path')
    def test_user_creation_in_graph(self, mock_create_learning_path, learning_path_service,
                                   mock_user, sample_learning_path_json):
        """Test that user entity is created in the graph."""
        mock_db = AsyncMock()
        topic = "machine learning"
        mock_db_learning_path = Mock()
        mock_create_learning_path.return_value = mock_db_learning_path
        
        captured_graphs = []
        
        def capture_graph(user_id, graph):
            captured_graphs.append(graph)
        
        with patch.object(learning_path_service.storage, 'save_user_graph', side_effect=capture_graph):
            learning_path_service.parse_and_save_learning_path(
                mock_db, sample_learning_path_json, topic, mock_user
            )
        
        # Verify user was added to graph
        assert len(captured_graphs) > 0
        captured_graph = captured_graphs[0]
        user_uri = learning_path_service.kg_base.ONT[f"user_{mock_user.id}"]
        assert (user_uri, RDF.type, learning_path_service.kg_base.ONT.User) in captured_graph

    @patch('app.features.learning_path.service.crud.create_learning_path')
    def test_user_follows_path_relationship(self, mock_create_learning_path, learning_path_service,
                                           mock_user, sample_learning_path_json):
        """Test that user is linked to learning path with followsPath property."""
        mock_db = AsyncMock()
        topic = "machine learning"
        mock_db_learning_path = Mock()
        mock_create_learning_path.return_value = mock_db_learning_path
        
        captured_graphs = []
        
        def capture_graph(user_id, graph):
            captured_graphs.append(graph)
        
        with patch.object(learning_path_service.storage, 'save_user_graph', side_effect=capture_graph):
            learning_path_service.parse_and_save_learning_path(
                mock_db, sample_learning_path_json, topic, mock_user
            )
        
        # Verify followsPath relationship
        assert len(captured_graphs) > 0
        captured_graph = captured_graphs[0]
        user_uri = learning_path_service.kg_base.ONT[f"user_{mock_user.id}"]
        follows_triples = list(captured_graph.triples(
            (user_uri, learning_path_service.kg_base.ONT.followsPath, None)
        ))
        assert len(follows_triples) == 1

    @patch('app.features.learning_path.service.crud.create_learning_path')
    def test_database_record_creation(self, mock_create_learning_path, learning_path_service,
                                     mock_user, sample_learning_path_json):
        """Test that database record is created with correct data."""
        mock_db = AsyncMock()
        topic = "machine learning"
        mock_db_learning_path = Mock()
        mock_create_learning_path.return_value = mock_db_learning_path
        
        with patch.object(learning_path_service.storage, 'save_user_graph'):
            learning_path_service.parse_and_save_learning_path(
                mock_db, sample_learning_path_json, topic, mock_user
            )
        
        # Verify create_learning_path was called with correct parameters
        call_args = mock_create_learning_path.call_args
        assert call_args[0][0] == mock_db  # First arg is db session
        
        # Verify LearningPathCreate schema
        learning_path_create = call_args[0][1]
        assert isinstance(learning_path_create, LearningPathCreate)
        assert learning_path_create.user_id == mock_user.id
        assert learning_path_create.topic == topic

    @patch('app.features.learning_path.service.crud.create_learning_path')
    def test_graph_storage_with_correct_user_id(self, mock_create_learning_path, learning_path_service,
                                                mock_user, sample_learning_path_json):
        """Test that graph is saved with correct user ID."""
        mock_db = AsyncMock()
        topic = "test topic"
        mock_db_learning_path = Mock()
        mock_create_learning_path.return_value = mock_db_learning_path
        
        with patch.object(learning_path_service.storage, 'save_user_graph') as mock_save:
            learning_path_service.parse_and_save_learning_path(
                mock_db, sample_learning_path_json, topic, mock_user
            )
        
        # Verify save_user_graph was called with string user_id
        mock_save.assert_called_once()
        assert mock_save.call_args[0][0] == str(mock_user.id)

    @patch('app.features.learning_path.service.crud.create_learning_path')
    def test_complete_graph_structure(self, mock_create_learning_path, learning_path_service,
                                     mock_user, sample_learning_path_json):
        """Test that saved graph contains all expected triples."""
        mock_db = AsyncMock()
        topic = "machine learning"
        mock_db_learning_path = Mock()
        mock_create_learning_path.return_value = mock_db_learning_path
        
        captured_graphs = []
        
        def capture_graph(user_id, graph):
            captured_graphs.append(graph)
        
        with patch.object(learning_path_service.storage, 'save_user_graph', side_effect=capture_graph):
            learning_path_service.parse_and_save_learning_path(
                mock_db, sample_learning_path_json, topic, mock_user
            )
        
        # Count different types of triples
        assert len(captured_graphs) > 0
        captured_graph = captured_graphs[0]
        learning_path_triples = list(captured_graph.triples(
            (None, RDF.type, learning_path_service.kg_base.ONT.LearningPath)
        ))
        concept_triples = list(captured_graph.triples(
            (None, RDF.type, learning_path_service.kg_base.ONT.Concept)
        ))
        user_triples = list(captured_graph.triples(
            (None, RDF.type, learning_path_service.kg_base.ONT.User)
        ))
        
        assert len(learning_path_triples) == 1
        assert len(concept_triples) == len(sample_learning_path_json)
        assert len(user_triples) == 1

    @patch('app.features.learning_path.service.crud.create_learning_path')
    def test_empty_prerequisites_handling(self, mock_create_learning_path, learning_path_service,
                                         mock_user):
        """Test handling of concepts with empty prerequisites list."""
        mock_db = AsyncMock()
        topic = "test"
        json_data = [{"concept": "Test Concept", "prerequisites": []}]
        mock_db_learning_path = Mock()
        mock_create_learning_path.return_value = mock_db_learning_path
        
        captured_graphs = []
        
        def capture_graph(user_id, graph):
            captured_graphs.append(graph)
        
        with patch.object(learning_path_service.storage, 'save_user_graph', side_effect=capture_graph):
            learning_path_service.parse_and_save_learning_path(
                mock_db, json_data, topic, mock_user
            )
        
        # Verify no prerequisite triples
        assert len(captured_graphs) > 0
        captured_graph = captured_graphs[0]
        prereq_triples = list(captured_graph.triples(
            (None, learning_path_service.kg_base.ONT.hasPrerequisite, None)
        ))
        assert len(prereq_triples) == 0

    @patch('app.features.learning_path.service.crud.create_learning_path')
    def test_multiple_users_different_graphs(self, mock_create_learning_path, learning_path_service,
                                            sample_learning_path_json):
        """Test that different users get separate graph files."""
        mock_db = AsyncMock()
        topic = "test"
        mock_db_learning_path = Mock()
        mock_create_learning_path.return_value = mock_db_learning_path
        
        # Create two different users
        user1 = Mock(spec=User)
        user1.id = 1
        user2 = Mock(spec=User)
        user2.id = 2
        
        with patch.object(learning_path_service.storage, 'save_user_graph') as mock_save:
            # Save for user 1
            learning_path_service.parse_and_save_learning_path(
                mock_db, sample_learning_path_json, topic, user1
            )
            first_call_user_id = mock_save.call_args[0][0]
            
            # Save for user 2
            learning_path_service.parse_and_save_learning_path(
                mock_db, sample_learning_path_json, topic, user2
            )
            second_call_user_id = mock_save.call_args[0][0]
        
        # Verify different user IDs were used
        assert first_call_user_id == "1"
        assert second_call_user_id == "2"
        assert first_call_user_id != second_call_user_id


# ===== Integration Tests =====

class TestIntegration:
    """Integration tests combining multiple functions."""

    @patch('app.features.learning_path.service.crud.create_learning_path')
    def test_full_workflow(self, mock_create_learning_path, learning_path_service,
                          mock_user, sample_learning_path_json):
        """Test complete workflow from JSON to saved graph and DB record."""
        mock_db = AsyncMock()
        topic = "machine learning"
        mock_db_learning_path = Mock()
        mock_db_learning_path.id = 1
        mock_db_learning_path.topic = topic
        mock_create_learning_path.return_value = mock_db_learning_path
        
        # Step 1: Convert JSON to RDF
        graph, learning_path_uri = learning_path_service.convert_learning_path_json_to_rdf_graph(
            sample_learning_path_json, topic
        )
        
        # Verify graph creation
        assert len(graph) > 0
        assert isinstance(learning_path_uri, URIRef)
        
        # Step 2: Save to storage and DB
        with patch.object(learning_path_service.storage, 'save_user_graph'):
            result = learning_path_service.parse_and_save_learning_path(
                mock_db, sample_learning_path_json, topic, mock_user
            )
        
        # Verify final result
        assert result == mock_db_learning_path
        mock_create_learning_path.assert_called_once()

    @patch('app.features.learning_path.service.crud.create_learning_path')
    def test_graph_serialization(self, mock_create_learning_path, learning_path_service,
                                mock_user, sample_learning_path_json):
        """Test that graph can be serialized to turtle format."""
        mock_db = AsyncMock()
        topic = "test"
        mock_db_learning_path = Mock()
        mock_create_learning_path.return_value = mock_db_learning_path
        
        captured_graphs = []
        
        def capture_graph(user_id, graph):
            captured_graphs.append(graph)
        
        with patch.object(learning_path_service.storage, 'save_user_graph', side_effect=capture_graph):
            learning_path_service.parse_and_save_learning_path(
                mock_db, sample_learning_path_json, topic, mock_user
            )
        
        # Try to serialize to turtle format
        assert len(captured_graphs) > 0
        captured_graph = captured_graphs[0]
        try:
            turtle_output = captured_graph.serialize(format='turtle')
            assert len(turtle_output) > 0
            assert isinstance(turtle_output, (str, bytes))
        except Exception as e:
            pytest.fail(f"Graph serialization failed: {e}")
