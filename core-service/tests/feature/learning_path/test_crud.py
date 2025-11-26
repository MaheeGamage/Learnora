"""
Unit tests for Learning Path CRUD operations.

Tests all CRUD operations including:
- Create operations
- Read operations (by ID, thread ID, user ID, topic)
- Update operations
- Delete operations
"""

import pytest
from unittest.mock import Mock, AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.features.learning_path import crud
from app.features.learning_path.models import LearningPath
from app.features.learning_path.schemas import LearningPathCreate, LearningPathUpdate


# ===== Fixtures =====

@pytest.fixture
def mock_db():
    """Create a mock AsyncSession for testing."""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def sample_learning_path_data():
    """Sample learning path data."""
    return {
        "id": 1,
        "topic": "Machine Learning Basics",
        "graph_uri": "http://example.com/ml-basics",
        "conversation_thread_id": ["thread-123", "thread-456"],
        "user_id": 1,
        "created_at": datetime.now(),
        "updated_at": None
    }


@pytest.fixture
def sample_learning_path_model(sample_learning_path_data):
    """Create a mock LearningPath model instance."""
    lp = Mock(spec=LearningPath)
    for key, value in sample_learning_path_data.items():
        setattr(lp, key, value)
    return lp


@pytest.fixture
def learning_path_create_schema():
    """Sample LearningPathCreate schema."""
    return LearningPathCreate(
        topic="Deep Learning",
        user_id=1,
        graph_uri="http://example.com/dl",
        conversation_thread_id=["thread-789"]
    )


# ===== Tests for Create Operations =====

class TestCreateOperations:
    """Tests for create CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_learning_path_success(self, mock_db, learning_path_create_schema):
        """Test successful creation of learning path."""
        # Setup mock
        expected_lp = Mock(spec=LearningPath)
        expected_lp.id = 1
        expected_lp.topic = learning_path_create_schema.topic
        expected_lp.user_id = learning_path_create_schema.user_id
        
        mock_db.add = Mock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        # Mock the LearningPath constructor
        with pytest.mock.patch('app.features.learning_path.crud.LearningPath', return_value=expected_lp):
            result = await crud.create_learning_path(mock_db, learning_path_create_schema)
        
        # Assertions
        mock_db.add.assert_called_once_with(expected_lp)
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(expected_lp)
        assert result == expected_lp

    @pytest.mark.asyncio
    async def test_create_learning_path_with_optional_fields(self, mock_db):
        """Test creation with optional fields set to None."""
        schema = LearningPathCreate(
            topic="Test Topic",
            user_id=1,
            graph_uri=None,
            conversation_thread_id=None
        )
        
        expected_lp = Mock(spec=LearningPath)
        expected_lp.id = 1
        
        mock_db.add = Mock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        with pytest.mock.patch('app.features.learning_path.crud.LearningPath', return_value=expected_lp):
            result = await crud.create_learning_path(mock_db, schema)
        
        assert result == expected_lp
        mock_db.commit.assert_called_once()


# ===== Tests for Read Operations =====

class TestReadOperations:
    """Tests for read CRUD operations."""

    @pytest.mark.asyncio
    async def test_get_learning_path_by_id_found(self, mock_db, sample_learning_path_model):
        """Test getting learning path by ID when it exists."""
        # Setup mock
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = sample_learning_path_model
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        # Execute
        result = await crud.get_learning_path_by_id(mock_db, 1)
        
        # Assertions
        assert result == sample_learning_path_model
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_learning_path_by_id_not_found(self, mock_db):
        """Test getting learning path by ID when it doesn't exist."""
        # Setup mock
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        # Execute
        result = await crud.get_learning_path_by_id(mock_db, 999)
        
        # Assertions
        assert result is None
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_learning_path_by_thread_id_found(self, mock_db, sample_learning_path_model):
        """Test getting learning path by thread ID when it exists."""
        # Setup mock
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = sample_learning_path_model
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        # Execute
        result = await crud.get_learning_path_by_thread_id(mock_db, "thread-123")
        
        # Assertions
        assert result == sample_learning_path_model
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_learning_path_by_thread_id_not_found(self, mock_db):
        """Test getting learning path by thread ID when it doesn't exist."""
        # Setup mock
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        # Execute
        result = await crud.get_learning_path_by_thread_id(mock_db, "nonexistent-thread")
        
        # Assertions
        assert result is None

    @pytest.mark.asyncio
    async def test_get_learning_paths_by_user_id(self, mock_db):
        """Test getting all learning paths for a user."""
        # Create mock learning paths
        lp1 = Mock(spec=LearningPath)
        lp1.id = 1
        lp1.user_id = 1
        
        lp2 = Mock(spec=LearningPath)
        lp2.id = 2
        lp2.user_id = 1
        
        # Setup mock
        mock_scalars = Mock()
        mock_scalars.all.return_value = [lp1, lp2]
        mock_result = Mock()
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        # Execute
        result = await crud.get_learning_paths_by_user_id(mock_db, 1)
        
        # Assertions
        assert len(result) == 2
        assert result[0] == lp1
        assert result[1] == lp2
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_learning_paths_by_user_id_with_pagination(self, mock_db):
        """Test getting learning paths with pagination."""
        # Setup mock
        mock_scalars = Mock()
        mock_scalars.all.return_value = []
        mock_result = Mock()
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        # Execute
        result = await crud.get_learning_paths_by_user_id(mock_db, 1, skip=10, limit=5)
        
        # Assertions
        assert isinstance(result, list)
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_learning_path_by_topic_and_user_found(self, mock_db, sample_learning_path_model):
        """Test getting learning path by topic and user when it exists."""
        # Setup mock
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = sample_learning_path_model
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        # Execute
        result = await crud.get_learning_path_by_topic_and_user(mock_db, "Machine Learning Basics", 1)
        
        # Assertions
        assert result == sample_learning_path_model
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_learning_path_by_topic_and_user_not_found(self, mock_db):
        """Test getting learning path by topic and user when it doesn't exist."""
        # Setup mock
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        # Execute
        result = await crud.get_learning_path_by_topic_and_user(mock_db, "Nonexistent Topic", 1)
        
        # Assertions
        assert result is None

    @pytest.mark.asyncio
    async def test_get_all_learning_paths(self, mock_db):
        """Test getting all learning paths."""
        # Create mock learning paths
        lp1 = Mock(spec=LearningPath)
        lp2 = Mock(spec=LearningPath)
        lp3 = Mock(spec=LearningPath)
        
        # Setup mock
        mock_scalars = Mock()
        mock_scalars.all.return_value = [lp1, lp2, lp3]
        mock_result = Mock()
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        # Execute
        result = await crud.get_all_learning_paths(mock_db)
        
        # Assertions
        assert len(result) == 3
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_count_learning_paths_by_user(self, mock_db):
        """Test counting learning paths for a user."""
        # Setup mock
        mock_result = Mock()
        mock_result.scalar_one.return_value = 5
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        # Execute
        result = await crud.count_learning_paths_by_user(mock_db, 1)
        
        # Assertions
        assert result == 5
        mock_db.execute.assert_called_once()


# ===== Tests for Update Operations =====

class TestUpdateOperations:
    """Tests for update CRUD operations."""

    @pytest.mark.asyncio
    async def test_update_learning_path_by_id_success(self, mock_db, sample_learning_path_model):
        """Test updating learning path by ID successfully."""
        # Setup mock
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = sample_learning_path_model
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        update_data = LearningPathUpdate(topic="Updated Topic")
        
        # Execute
        result = await crud.update_learning_path_by_id(mock_db, 1, update_data)
        
        # Assertions
        assert result == sample_learning_path_model
        assert sample_learning_path_model.topic == "Updated Topic"
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_learning_path_by_id_not_found(self, mock_db):
        """Test updating learning path when it doesn't exist."""
        # Setup mock
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        update_data = LearningPathUpdate(topic="Updated Topic")
        
        # Execute
        result = await crud.update_learning_path_by_id(mock_db, 999, update_data)
        
        # Assertions
        assert result is None
        mock_db.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_learning_path_by_thread_id_success(self, mock_db, sample_learning_path_model):
        """Test updating learning path by thread ID."""
        # Setup mock
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = sample_learning_path_model
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        update_data = LearningPathUpdate(topic="Updated via Thread")
        
        # Execute
        result = await crud.update_learning_path(mock_db, "thread-123", update_data)
        
        # Assertions
        assert result == sample_learning_path_model
        assert sample_learning_path_model.topic == "Updated via Thread"
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_thread_to_learning_path_success(self, mock_db, sample_learning_path_model):
        """Test adding a thread ID to learning path."""
        # Setup mock
        sample_learning_path_model.conversation_thread_id = ["thread-123"]
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = sample_learning_path_model
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        # Execute
        result = await crud.add_thread_to_learning_path(mock_db, 1, "thread-new")
        
        # Assertions
        assert result == sample_learning_path_model
        assert "thread-new" in sample_learning_path_model.conversation_thread_id
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_thread_to_learning_path_with_none_list(self, mock_db, sample_learning_path_model):
        """Test adding thread when thread list is None."""
        # Setup mock
        sample_learning_path_model.conversation_thread_id = None
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = sample_learning_path_model
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        # Execute
        result = await crud.add_thread_to_learning_path(mock_db, 1, "thread-first")
        
        # Assertions
        assert result == sample_learning_path_model
        assert sample_learning_path_model.conversation_thread_id == ["thread-first"]
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_thread_duplicate_not_added(self, mock_db, sample_learning_path_model):
        """Test that duplicate thread IDs are not added."""
        # Setup mock
        sample_learning_path_model.conversation_thread_id = ["thread-123"]
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = sample_learning_path_model
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        # Execute
        await crud.add_thread_to_learning_path(mock_db, 1, "thread-123")
        
        # Assertions
        assert len(sample_learning_path_model.conversation_thread_id) == 1
        mock_db.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_graph_uri_success(self, mock_db, sample_learning_path_model):
        """Test updating graph URI."""
        # Setup mock
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = sample_learning_path_model
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        new_uri = "http://example.com/new-graph"
        
        # Execute
        result = await crud.update_graph_uri(mock_db, 1, new_uri)
        
        # Assertions
        assert result == sample_learning_path_model
        assert sample_learning_path_model.graph_uri == new_uri
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_graph_uri_not_found(self, mock_db):
        """Test updating graph URI when learning path doesn't exist."""
        # Setup mock
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        # Execute
        result = await crud.update_graph_uri(mock_db, 999, "http://example.com/new")
        
        # Assertions
        assert result is None
        mock_db.commit.assert_not_called()


# ===== Tests for Delete Operations =====

class TestDeleteOperations:
    """Tests for delete CRUD operations."""

    @pytest.mark.asyncio
    async def test_delete_learning_path_by_id_success(self, mock_db, sample_learning_path_model):
        """Test deleting learning path by ID successfully."""
        # Setup mock
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = sample_learning_path_model
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_db.delete = AsyncMock()
        mock_db.commit = AsyncMock()
        
        # Execute
        result = await crud.delete_learning_path_by_id(mock_db, 1)
        
        # Assertions
        assert result is True
        mock_db.delete.assert_called_once_with(sample_learning_path_model)
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_learning_path_by_id_not_found(self, mock_db):
        """Test deleting learning path when it doesn't exist."""
        # Setup mock
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        # Execute
        result = await crud.delete_learning_path_by_id(mock_db, 999)
        
        # Assertions
        assert result is False
        mock_db.delete.assert_not_called()
        mock_db.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_delete_learning_path_by_thread_id_success(self, mock_db, sample_learning_path_model):
        """Test deleting learning path by thread ID."""
        # Setup mock
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = sample_learning_path_model
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_db.delete = AsyncMock()
        mock_db.commit = AsyncMock()
        
        # Execute
        result = await crud.delete_learning_path(mock_db, "thread-123")
        
        # Assertions
        assert result is True
        mock_db.delete.assert_called_once()
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_learning_paths_by_user_success(self, mock_db):
        """Test deleting all learning paths for a user."""
        # Setup mock
        mock_result = Mock()
        mock_result.rowcount = 3
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_db.commit = AsyncMock()
        
        # Execute
        result = await crud.delete_learning_paths_by_user(mock_db, 1)
        
        # Assertions
        assert result == 3
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_learning_paths_by_user_none_found(self, mock_db):
        """Test deleting learning paths when user has none."""
        # Setup mock
        mock_result = Mock()
        mock_result.rowcount = 0
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_db.commit = AsyncMock()
        
        # Execute
        result = await crud.delete_learning_paths_by_user(mock_db, 999)
        
        # Assertions
        assert result == 0
        mock_db.commit.assert_called_once()


# ===== Integration Tests =====

class TestCRUDIntegration:
    """Integration tests for CRUD operations workflow."""

    @pytest.mark.asyncio
    async def test_create_read_update_delete_workflow(self, mock_db):
        """Test complete CRUD workflow."""
        # Create
        create_schema = LearningPathCreate(
            topic="Test Topic",
            user_id=1,
            graph_uri="http://example.com/test"
        )
        
        created_lp = Mock(spec=LearningPath)
        created_lp.id = 1
        created_lp.topic = create_schema.topic
        
        mock_db.add = Mock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        with pytest.mock.patch('app.features.learning_path.crud.LearningPath', return_value=created_lp):
            created = await crud.create_learning_path(mock_db, create_schema)
        
        assert created == created_lp
        
        # Read
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = created_lp
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        read = await crud.get_learning_path_by_id(mock_db, 1)
        assert read == created_lp
        
        # Update
        update_schema = LearningPathUpdate(topic="Updated Topic")
        created_lp.topic = "Updated Topic"
        
        updated = await crud.update_learning_path_by_id(mock_db, 1, update_schema)
        assert updated.topic == "Updated Topic"
        
        # Delete
        mock_db.delete = AsyncMock()
        deleted = await crud.delete_learning_path_by_id(mock_db, 1)
        assert deleted is True

    @pytest.mark.asyncio
    async def test_user_scoped_operations(self, mock_db):
        """Test user-scoped CRUD operations."""
        user_id = 1
        
        # Create multiple learning paths for user
        lp1 = Mock(spec=LearningPath)
        lp1.id = 1
        lp1.user_id = user_id
        
        lp2 = Mock(spec=LearningPath)
        lp2.id = 2
        lp2.user_id = user_id
        
        # Get by user
        mock_scalars = Mock()
        mock_scalars.all.return_value = [lp1, lp2]
        mock_result = Mock()
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        paths = await crud.get_learning_paths_by_user_id(mock_db, user_id)
        assert len(paths) == 2
        
        # Count by user
        mock_result = Mock()
        mock_result.scalar_one.return_value = 2
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        count = await crud.count_learning_paths_by_user(mock_db, user_id)
        assert count == 2
        
        # Delete by user
        mock_result = Mock()
        mock_result.rowcount = 2
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_db.commit = AsyncMock()
        
        deleted_count = await crud.delete_learning_paths_by_user(mock_db, user_id)
        assert deleted_count == 2
