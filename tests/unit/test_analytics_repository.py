"""
Comprehensive unit tests for Analytics Repository layer.

Tests cover:
- save_result
- get_result
- delete_result
- query_results
- invalid input
- concurrency
- persistence contracts
"""

from datetime import datetime, timedelta
from uuid import uuid4

import pytest

from apps.graph_engine.analytics.interfaces import AlgorithmResult
from apps.graph_engine.analytics.repositories import (
    AnalyticsRepository,
    InMemoryAnalyticsRepository,
    StoredResult,
    create_repository,
    get_default_repository,
    set_default_repository,
)

# ============================================================================
# Save Result Tests
# ============================================================================


class TestSaveResult:
    """Tests for save_result method."""

    def test_save_result_returns_id(self):
        """Test that save_result returns a valid ID string."""
        repository = InMemoryAnalyticsRepository()

        result = AlgorithmResult(
            algorithm_name="test_algo",
            graph_id=uuid4(),
            execution_time_ms=100,
            results={"data": "value"},
            metadata={"version": "1.0"},
        )

        result_id = repository.save_result(result)

        assert isinstance(result_id, str)
        assert len(result_id) > 0

    def test_save_result_stores_result(self):
        """Test that save_result actually stores the result."""
        repository = InMemoryAnalyticsRepository()
        graph_id = uuid4()

        result = AlgorithmResult(
            algorithm_name="test_algo",
            graph_id=graph_id,
            execution_time_ms=100,
            results={"data": "value"},
            metadata={"version": "1.0"},
        )

        result_id = repository.save_result(result)
        retrieved = repository.get_result(result_id)

        assert retrieved is not None
        assert retrieved.algorithm_name == "test_algo"
        assert retrieved.graph_id == graph_id
        assert retrieved.results == {"data": "value"}

    def test_save_result_indexes_by_graph(self):
        """Test that save_result creates graph index."""
        repository = InMemoryAnalyticsRepository()
        graph_id = uuid4()

        result = AlgorithmResult(
            algorithm_name="test_algo",
            graph_id=graph_id,
            execution_time_ms=100,
            results={"data": "value"},
            metadata={},
        )

        repository.save_result(result)

        # Check that graph is indexed
        assert graph_id in repository._by_graph
        assert "test_algo" in repository._by_graph[graph_id]

    def test_save_result_indexes_by_algorithm(self):
        """Test that save_result creates algorithm index."""
        repository = InMemoryAnalyticsRepository()

        result = AlgorithmResult(
            algorithm_name="test_algo",
            graph_id=uuid4(),
            execution_time_ms=100,
            results={"data": "value"},
            metadata={},
        )

        result_id = repository.save_result(result)

        # Check that algorithm is indexed
        assert "test_algo" in repository._by_algorithm
        assert result_id in repository._by_algorithm["test_algo"]

    def test_save_multiple_results_same_graph(self):
        """Test saving multiple results for the same graph."""
        repository = InMemoryAnalyticsRepository()
        graph_id = uuid4()

        result1 = AlgorithmResult(
            algorithm_name="algo1",
            graph_id=graph_id,
            execution_time_ms=100,
            results={"data": "value1"},
            metadata={},
        )

        result2 = AlgorithmResult(
            algorithm_name="algo2",
            graph_id=graph_id,
            execution_time_ms=200,
            results={"data": "value2"},
            metadata={},
        )

        id1 = repository.save_result(result1)
        id2 = repository.save_result(result2)

        assert id1 != id2
        assert len(repository._by_graph[graph_id]) == 2


# ============================================================================
# Get Result Tests
# ============================================================================


class TestGetResult:
    """Tests for get_result method."""

    def test_get_result_returns_saved_result(self):
        """Test that get_result returns previously saved result."""
        repository = InMemoryAnalyticsRepository()

        result = AlgorithmResult(
            algorithm_name="test_algo",
            graph_id=uuid4(),
            execution_time_ms=100,
            results={"data": "value"},
            metadata={},
        )

        result_id = repository.save_result(result)
        retrieved = repository.get_result(result_id)

        assert retrieved is not None
        assert retrieved.algorithm_name == "test_algo"
        assert retrieved.results == {"data": "value"}

    def test_get_result_nonexistent_returns_none(self):
        """Test that get_result returns None for nonexistent ID."""
        repository = InMemoryAnalyticsRepository()

        result = repository.get_result("nonexistent_id")

        assert result is None

    def test_get_result_empty_string_returns_none(self):
        """Test that get_result handles empty string ID."""
        repository = InMemoryAnalyticsRepository()

        result = repository.get_result("")

        assert result is None

    def test_get_result_preserves_all_fields(self):
        """Test that get_result preserves all result fields."""
        repository = InMemoryAnalyticsRepository()
        graph_id = uuid4()

        original = AlgorithmResult(
            algorithm_name="test_algo",
            graph_id=graph_id,
            execution_time_ms=123,
            results={"complex": {"nested": "data"}},
            metadata={
                "version": "2.0",
                "timestamp": "2024-01-01",
                "custom": "value",
            },
        )

        result_id = repository.save_result(original)
        retrieved = repository.get_result(result_id)

        assert retrieved.algorithm_name == original.algorithm_name
        assert retrieved.graph_id == original.graph_id
        assert retrieved.execution_time_ms == original.execution_time_ms
        assert retrieved.results == original.results
        assert retrieved.metadata == original.metadata


# ============================================================================
# Get Latest Result Tests
# ============================================================================


class TestGetLatestResult:
    """Tests for get_latest_result method."""

    def test_get_latest_result_single_result(self):
        """Test getting latest result with only one result."""
        repository = InMemoryAnalyticsRepository()
        graph_id = uuid4()

        result = AlgorithmResult(
            algorithm_name="test_algo",
            graph_id=graph_id,
            execution_time_ms=100,
            results={"data": "value"},
            metadata={},
        )

        repository.save_result(result)
        latest = repository.get_latest_result(graph_id, "test_algo")

        assert latest is not None
        assert latest.algorithm_name == "test_algo"

    def test_get_latest_result_returns_most_recent(self):
        """Test that get_latest_result returns the most recent result."""
        repository = InMemoryAnalyticsRepository()
        graph_id = uuid4()

        # Save first result
        result1 = AlgorithmResult(
            algorithm_name="test_algo",
            graph_id=graph_id,
            execution_time_ms=100,
            results={"data": "value1"},
            metadata={},
        )

        repository.save_result(result1)

        # Small delay to ensure different timestamps
        import time

        time.sleep(0.01)

        # Save second result (more recent)
        result2 = AlgorithmResult(
            algorithm_name="test_algo",
            graph_id=graph_id,
            execution_time_ms=200,
            results={"data": "value2"},
            metadata={},
        )

        repository.save_result(result2)

        latest = repository.get_latest_result(graph_id, "test_algo")

        assert latest is not None
        assert latest.results == {"data": "value2"}

    def test_get_latest_result_nonexistent_graph(self):
        """Test get_latest_result for nonexistent graph."""
        repository = InMemoryAnalyticsRepository()

        result = repository.get_latest_result(uuid4(), "test_algo")

        assert result is None

    def test_get_latest_result_empty_result_list(self):
        """Test get_latest_result when graph has algorithm entry but empty result list."""
        repository = InMemoryAnalyticsRepository()
        graph_id = uuid4()

        # Manually create empty algorithm entry (edge case)
        repository._by_graph[graph_id] = {"test_algo": []}

        result = repository.get_latest_result(graph_id, "test_algo")

        assert result is None

    def test_get_latest_result_nonexistent_algorithm(self):
        """Test get_latest_result for nonexistent algorithm."""
        repository = InMemoryAnalyticsRepository()
        graph_id = uuid4()

        # Save result with different algorithm
        result = AlgorithmResult(
            algorithm_name="other_algo",
            graph_id=graph_id,
            execution_time_ms=100,
            results={"data": "value"},
            metadata={},
        )

        repository.save_result(result)

        # Try to get latest for different algorithm
        latest = repository.get_latest_result(graph_id, "test_algo")

        assert latest is None

    def test_get_latest_result_multiple_algorithms_same_graph(self):
        """Test get_latest_result with multiple algorithms on same graph."""
        repository = InMemoryAnalyticsRepository()
        graph_id = uuid4()

        result1 = AlgorithmResult(
            algorithm_name="algo1",
            graph_id=graph_id,
            execution_time_ms=100,
            results={"data": "value1"},
            metadata={},
        )

        result2 = AlgorithmResult(
            algorithm_name="algo2",
            graph_id=graph_id,
            execution_time_ms=200,
            results={"data": "value2"},
            metadata={},
        )

        repository.save_result(result1)
        repository.save_result(result2)

        # Should get correct result for each algorithm
        latest1 = repository.get_latest_result(graph_id, "algo1")
        latest2 = repository.get_latest_result(graph_id, "algo2")

        assert latest1 is not None
        assert latest1.algorithm_name == "algo1"
        assert latest2 is not None
        assert latest2.algorithm_name == "algo2"


# ============================================================================
# Get Results By Date Range Tests
# ============================================================================


class TestGetResultsByDateRange:
    """Tests for get_results_by_date_range method."""

    def test_get_results_in_range(self):
        """Test getting results within date range."""
        repository = InMemoryAnalyticsRepository()
        graph_id = uuid4()

        now = datetime.utcnow()

        # Create result within range
        result = AlgorithmResult(
            algorithm_name="test_algo",
            graph_id=graph_id,
            execution_time_ms=100,
            results={"data": "value"},
            metadata={"created_at": now},
        )

        repository.save_result(result)

        # Query for range that includes the result
        start = now - timedelta(hours=1)
        end = now + timedelta(hours=1)

        results = repository.get_results_by_date_range(graph_id, start, end)

        assert len(results) == 1
        assert results[0].algorithm_name == "test_algo"

    def test_get_results_empty_range(self):
        """Test getting results with empty date range."""
        repository = InMemoryAnalyticsRepository()
        graph_id = uuid4()

        result = AlgorithmResult(
            algorithm_name="test_algo",
            graph_id=graph_id,
            execution_time_ms=100,
            results={"data": "value"},
            metadata={"created_at": datetime.utcnow()},
        )

        repository.save_result(result)

        # Query for range that doesn't include any results
        start = datetime.utcnow() + timedelta(hours=1)
        end = datetime.utcnow() + timedelta(hours=2)

        results = repository.get_results_by_date_range(graph_id, start, end)

        assert len(results) == 0

    def test_get_results_end_before_created_at(self):
        """Test when end_date is before result creation time."""
        repository = InMemoryAnalyticsRepository()
        graph_id = uuid4()

        # Save result
        result = AlgorithmResult(
            algorithm_name="test_algo",
            graph_id=graph_id,
            execution_time_ms=100,
            results={"data": "value"},
            metadata={},
        )

        rid = repository.save_result(result)
        # Set creation time to now
        repository._results[rid].created_at = datetime.utcnow()

        # Query for range that ends before result was created
        start = datetime.utcnow() - timedelta(hours=2)
        end = datetime.utcnow() - timedelta(hours=1)

        results = repository.get_results_by_date_range(graph_id, start, end)

        assert len(results) == 0

    def test_get_results_start_after_created_at(self):
        """Test when start_date is after result creation time."""
        repository = InMemoryAnalyticsRepository()
        graph_id = uuid4()

        # Save result
        result = AlgorithmResult(
            algorithm_name="test_algo",
            graph_id=graph_id,
            execution_time_ms=100,
            results={"data": "value"},
            metadata={},
        )

        rid = repository.save_result(result)
        # Set creation time to old
        repository._results[rid].created_at = datetime.utcnow() - timedelta(hours=2)

        # Query for range that starts after result was created
        start = datetime.utcnow() - timedelta(hours=1)
        end = datetime.utcnow()

        results = repository.get_results_by_date_range(graph_id, start, end)

        assert len(results) == 0

    def test_delete_removes_from_graph_index(self):
        """Test that _delete_result properly cleans up graph index."""
        repository = InMemoryAnalyticsRepository()
        graph_id = uuid4()

        result = AlgorithmResult(
            algorithm_name="test_algo",
            graph_id=graph_id,
            execution_time_ms=100,
            results={"data": "value"},
            metadata={},
        )

        rid = repository.save_result(result)
        repository._delete_result(rid)

        # Verify graph index is cleaned up
        assert graph_id not in repository._by_graph

    def test_delete_removes_from_algorithm_index(self):
        """Test that _delete_result properly cleans up algorithm index."""
        repository = InMemoryAnalyticsRepository()
        graph_id = uuid4()

        result = AlgorithmResult(
            algorithm_name="test_algo",
            graph_id=graph_id,
            execution_time_ms=100,
            results={"data": "value"},
            metadata={},
        )

        rid = repository.save_result(result)
        repository._delete_result(rid)

        # Verify algorithm index is cleaned up
        assert "test_algo" not in repository._by_algorithm

    def test_delete_with_multiple_results_same_graph(self):
        """Test _delete_result when graph has multiple results."""
        repository = InMemoryAnalyticsRepository()
        graph_id = uuid4()

        result1 = AlgorithmResult(
            algorithm_name="algo1",
            graph_id=graph_id,
            execution_time_ms=100,
            results={"data": "value1"},
            metadata={},
        )

        result2 = AlgorithmResult(
            algorithm_name="algo2",
            graph_id=graph_id,
            execution_time_ms=100,
            results={"data": "value2"},
            metadata={},
        )

        rid1 = repository.save_result(result1)
        repository.save_result(result2)

        # Delete first result
        repository._delete_result(rid1)

        # Verify graph index still exists (has algo2)
        assert graph_id in repository._by_graph
        assert "algo1" not in repository._by_graph[graph_id]
        assert "algo2" in repository._by_graph[graph_id]

    def test_get_results_sorted_by_date(self):
        """Test that results are returned sorted by date."""
        repository = InMemoryAnalyticsRepository()
        graph_id = uuid4()

        now = datetime.utcnow()

        # Create results at different times
        result1 = AlgorithmResult(
            algorithm_name="test_algo",
            graph_id=graph_id,
            execution_time_ms=100,
            results={"index": 1},
            metadata={"created_at": now - timedelta(hours=2)},
        )

        result2 = AlgorithmResult(
            algorithm_name="test_algo",
            graph_id=graph_id,
            execution_time_ms=100,
            results={"index": 2},
            metadata={"created_at": now - timedelta(hours=1)},
        )

        result3 = AlgorithmResult(
            algorithm_name="test_algo",
            graph_id=graph_id,
            execution_time_ms=100,
            results={"index": 3},
            metadata={"created_at": now},
        )

        repository.save_result(result1)
        repository.save_result(result2)
        repository.save_result(result3)

        # Query wide range
        start = now - timedelta(hours=3)
        end = now + timedelta(hours=1)

        results = repository.get_results_by_date_range(graph_id, start, end)

        # Should be sorted by creation time
        assert len(results) == 3
        assert results[0].results == {"index": 1}
        assert results[1].results == {"index": 2}
        assert results[2].results == {"index": 3}

    def test_get_results_multiple_graphs(self):
        """Test that results are filtered by graph ID."""
        repository = InMemoryAnalyticsRepository()

        graph1 = uuid4()
        graph2 = uuid4()

        now = datetime.utcnow()

        # Save results for both graphs
        result1 = AlgorithmResult(
            algorithm_name="test_algo",
            graph_id=graph1,
            execution_time_ms=100,
            results={"graph": 1},
            metadata={"created_at": now},
        )

        result2 = AlgorithmResult(
            algorithm_name="test_algo",
            graph_id=graph2,
            execution_time_ms=100,
            results={"graph": 2},
            metadata={"created_at": now},
        )

        repository.save_result(result1)
        repository.save_result(result2)

        # Query for graph1 only
        start = now - timedelta(hours=1)
        end = now + timedelta(hours=1)

        results = repository.get_results_by_date_range(graph1, start, end)

        assert len(results) == 1
        assert results[0].results == {"graph": 1}


# ============================================================================
# Delete Old Results Tests
# ============================================================================


class TestDeleteOldResults:
    """Tests for delete_old_results method."""

    def test_delete_nonexistent_result_id(self):
        """Test that _delete_result handles nonexistent ID gracefully."""
        repository = InMemoryAnalyticsRepository()

        # This should not raise an error
        repository._delete_result("nonexistent_id")

        assert len(repository._results) == 0

    def test_delete_old_results(self):
        """Test deleting results older than specified date."""
        repository = InMemoryAnalyticsRepository()
        graph_id = uuid4()

        now = datetime.utcnow()

        # Create old result (simulate old by using time-based creation)
        old_result = AlgorithmResult(
            algorithm_name="test_algo",
            graph_id=graph_id,
            execution_time_ms=100,
            results={"old": True},
            metadata={},
        )

        repository.save_result(old_result)

        # Manually set the creation time to old
        old_result_id = list(repository._results.keys())[-1]
        repository._results[old_result_id].created_at = now - timedelta(hours=2)

        # Create new result
        new_result = AlgorithmResult(
            algorithm_name="test_algo",
            graph_id=graph_id,
            execution_time_ms=100,
            results={"new": True},
            metadata={},
        )

        repository.save_result(new_result)

        # Delete results older than 1 hour
        cutoff = now - timedelta(hours=1)
        deleted_count = repository.delete_old_results(cutoff)

        assert deleted_count == 1

        # Verify old result is gone, new result remains
        results = list(repository._results.values())
        results_data = [r.result for r in results]

        assert any(r.results == {"new": True} for r in results_data)
        assert not any(r.results == {"old": True} for r in results_data)

    def test_delete_old_results_returns_count(self):
        """Test that delete_old_results returns correct count."""
        repository = InMemoryAnalyticsRepository()
        now = datetime.utcnow()

        # Create multiple old results
        result_ids = []
        for i in range(5):
            result = AlgorithmResult(
                algorithm_name="test_algo",
                graph_id=uuid4(),
                execution_time_ms=100,
                results={"index": i},
                metadata={},
            )
            rid = repository.save_result(result)
            result_ids.append(rid)
            # Manually set creation time to old
            repository._results[rid].created_at = now - timedelta(hours=2)

        # Delete results older than 1 hour
        cutoff = now - timedelta(hours=1)
        deleted_count = repository.delete_old_results(cutoff)

        assert deleted_count == 5
        assert len(repository._results) == 0

    def test_delete_old_results_nothing_to_delete(self):
        """Test delete_old_results when nothing needs deleting."""
        repository = InMemoryAnalyticsRepository()
        now = datetime.utcnow()

        result = AlgorithmResult(
            algorithm_name="test_algo",
            graph_id=uuid4(),
            execution_time_ms=100,
            results={"data": "value"},
            metadata={"created_at": now},
        )

        repository.save_result(result)

        # Try to delete results older than 1 hour (result is new)
        cutoff = now - timedelta(hours=1)
        deleted_count = repository.delete_old_results(cutoff)

        assert deleted_count == 0
        assert len(repository._results) == 1

    def test_delete_old_results_clears_indexes(self):
        """Test that delete_old_results clears indexes."""
        repository = InMemoryAnalyticsRepository()
        graph_id = uuid4()
        now = datetime.utcnow()

        # Create old result
        old_result = AlgorithmResult(
            algorithm_name="test_algo",
            graph_id=graph_id,
            execution_time_ms=100,
            results={"old": True},
            metadata={},
        )

        rid = repository.save_result(old_result)
        # Manually set creation time to old
        repository._results[rid].created_at = now - timedelta(hours=2)

        # Verify indexes exist
        assert graph_id in repository._by_graph
        assert "test_algo" in repository._by_algorithm

        # Delete old results
        cutoff = now - timedelta(hours=1)
        repository.delete_old_results(cutoff)

        # Verify indexes are cleared
        # Note: graph index might still exist but be empty
        assert len(repository._by_algorithm.get("test_algo", [])) == 0


# ============================================================================
# Clear Tests
# ============================================================================


class TestClear:
    """Tests for clear method."""

    def test_clear_removes_all_results(self):
        """Test that clear removes all stored results."""
        repository = InMemoryAnalyticsRepository()

        # Add multiple results
        for i in range(10):
            result = AlgorithmResult(
                algorithm_name="test_algo",
                graph_id=uuid4(),
                execution_time_ms=100,
                results={"index": i},
                metadata={},
            )
            repository.save_result(result)

        assert len(repository._results) == 10

        # Clear all
        repository.clear()

        assert len(repository._results) == 0
        assert len(repository._by_graph) == 0
        assert len(repository._by_algorithm) == 0

    def test_clear_empty_repository(self):
        """Test that clear works on empty repository."""
        repository = InMemoryAnalyticsRepository()

        repository.clear()

        assert len(repository._results) == 0


# ============================================================================
# Get Statistics Tests
# ============================================================================


class TestGetStatistics:
    """Tests for get_statistics method."""

    def test_get_statistics_empty_repository(self):
        """Test statistics for empty repository."""
        repository = InMemoryAnalyticsRepository()

        stats = repository.get_statistics()

        assert stats["total_results"] == 0
        assert stats["graphs_stored"] == 0
        assert stats["algorithms_stored"] == 0

    def test_get_statistics_with_data(self):
        """Test statistics with data in repository."""
        repository = InMemoryAnalyticsRepository()

        # Add results for 3 graphs and 2 algorithms
        graph1 = uuid4()
        graph2 = uuid4()
        graph3 = uuid4()

        repository.save_result(
            AlgorithmResult(
                algorithm_name="algo1",
                graph_id=graph1,
                execution_time_ms=100,
                results={},
                metadata={},
            )
        )

        repository.save_result(
            AlgorithmResult(
                algorithm_name="algo1",
                graph_id=graph2,
                execution_time_ms=100,
                results={},
                metadata={},
            )
        )

        repository.save_result(
            AlgorithmResult(
                algorithm_name="algo2",
                graph_id=graph3,
                execution_time_ms=100,
                results={},
                metadata={},
            )
        )

        stats = repository.get_statistics()

        assert stats["total_results"] == 3
        assert stats["graphs_stored"] == 3
        assert stats["algorithms_stored"] == 2


# ============================================================================
# Factory Functions Tests
# ============================================================================


class TestFactoryFunctions:
    """Tests for factory functions."""

    def test_create_repository_memory(self):
        """Test creating in-memory repository."""
        repository = create_repository("memory")

        assert isinstance(repository, InMemoryAnalyticsRepository)

    def test_create_repository_unsupported_type(self):
        """Test creating repository with unsupported type."""
        with pytest.raises(ValueError, match="Unsupported repository type"):
            create_repository("invalid_type")

    def test_create_repository_database_not_implemented(self):
        """Test that database repository raises NotImplementedError."""
        with pytest.raises(NotImplementedError):
            create_repository("database")

    def test_get_default_repository_creates_instance(self):
        """Test that get_default_repository creates instance if needed."""
        # Clear default repository
        set_default_repository(None)

        repository = get_default_repository()

        assert repository is not None
        assert isinstance(repository, InMemoryAnalyticsRepository)

    def test_set_default_repository(self):
        """Test setting default repository."""
        custom_repo = InMemoryAnalyticsRepository()

        set_default_repository(custom_repo)
        retrieved = get_default_repository()

        assert retrieved is custom_repo


# ============================================================================
# StoredResult Dataclass Tests
# ============================================================================


class TestStoredResult:
    """Tests for StoredResult dataclass."""

    def test_stored_result_creation(self):
        """Test creating StoredResult."""
        result = AlgorithmResult(
            algorithm_name="test",
            graph_id=uuid4(),
            execution_time_ms=100,
            results={"data": "value"},
            metadata={},
        )

        stored = StoredResult(id="test_id", result=result)

        assert stored.id == "test_id"
        assert stored.result is result
        assert isinstance(stored.created_at, datetime)

    def test_stored_result_custom_timestamp(self):
        """Test StoredResult with custom timestamp."""
        result = AlgorithmResult(
            algorithm_name="test",
            graph_id=uuid4(),
            execution_time_ms=100,
            results={"data": "value"},
            metadata={},
        )

        custom_time = datetime.utcnow()
        stored = StoredResult(id="test_id", result=result, created_at=custom_time)

        assert stored.created_at == custom_time


# ============================================================================
# Invalid Input Tests
# ============================================================================


class TestInvalidInput:
    """Tests for handling invalid input."""

    def test_get_result_none_id(self):
        """Test get_result with None ID."""
        repository = InMemoryAnalyticsRepository()

        result = repository.get_result(None)

        assert result is None

    def test_get_latest_result_none_graph_id(self):
        """Test get_latest_result with None graph ID."""
        repository = InMemoryAnalyticsRepository()

        result = repository.get_latest_result(None, "test_algo")

        assert result is None

    def test_get_latest_result_none_algorithm_name(self):
        """Test get_latest_result with None algorithm name."""
        repository = InMemoryAnalyticsRepository()
        graph_id = uuid4()

        result = repository.get_latest_result(graph_id, None)

        assert result is None
