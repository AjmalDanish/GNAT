"""
Unit tests for analytics cache and executor.

Tests caching, algorithm execution, and service orchestration.
"""

import time
from datetime import datetime, timedelta
from uuid import uuid4

import pytest

from apps.graph_engine.analytics.exceptions import (
    AlgorithmExecutionError,
    AlgorithmNotFoundError,
    AlgorithmTimeoutError,
    InvalidConfigError,
)
from apps.graph_engine.analytics.interfaces import (
    AlgorithmConfig,
    AlgorithmResult,
    CentralityAlgorithm,
)
from apps.graph_engine.analytics.registry import get_registry
from apps.graph_engine.analytics.services.executor import (
    AlgorithmExecutor,
    CacheAdapter,
    CacheConfig,
)


class MockAlgorithm(CentralityAlgorithm):
    """Mock algorithm for testing."""

    name = "mock_algorithm"
    category = "centrality"
    version = "1.0.0"
    description = "Mock algorithm"
    complexity_time = "O(V + E)"
    complexity_space = "O(V)"
    recommended_max_nodes = 100_000

    @classmethod
    def validate_config(cls, config):
        if not config.graph_id:
            return ["graph_id is required"]
        return []

    @classmethod
    def get_required_parameters(cls):
        return []

    @classmethod
    def get_optional_parameters(cls):
        return {"weighted": False}

    def compute(self, backend, config):
        return AlgorithmResult(
            algorithm_name=self.name,
            graph_id=config.graph_id,
            execution_time_ms=100,
            results={"node1": 0.5, "node2": 0.8},
        )

    def compute_for_node(self, backend, node_id, config):
        return 0.5

    def get_top_nodes(self, backend, n=10, config=None):
        return []


class FailingAlgorithm(CentralityAlgorithm):
    """Mock algorithm that always fails."""

    name = "failing_algorithm"
    category = "centrality"
    version = "1.0.0"
    description = "Failing algorithm for testing"
    complexity_time = "O(V + E)"
    complexity_space = "O(V)"
    recommended_max_nodes = 100_000

    @classmethod
    def validate_config(cls, config):
        return []

    @classmethod
    def get_required_parameters(cls):
        return []

    @classmethod
    def get_optional_parameters(cls):
        return {}

    def compute(self, backend, config):
        raise RuntimeError("Simulated failure")

    def compute_for_node(self, backend, node_id, config):
        return 0.5

    def get_top_nodes(self, backend, n=10, config=None):
        return []


class TestCacheConfig:
    """Tests for CacheConfig dataclass."""

    def test_default_config(self):
        """Test creating cache config with defaults."""
        config = CacheConfig()

        assert config.enabled is True
        assert config.ttl_seconds == 3600
        assert config.key_prefix == "graph_analytics:"
        assert config.max_size_bytes is None

    def test_custom_config(self):
        """Test creating cache config with custom values."""
        config = CacheConfig(
            enabled=False,
            ttl_seconds=7200,
            key_prefix="custom:",
            max_size_bytes=1024 * 1024 * 100,  # 100MB
        )

        assert config.enabled is False
        assert config.ttl_seconds == 7200
        assert config.key_prefix == "custom:"
        assert config.max_size_bytes == 1024 * 1024 * 100


class TestCacheAdapter:
    """Tests for CacheAdapter."""

    def test_get_nonexistent_key(self):
        """Test getting nonexistent key returns None."""
        cache = CacheAdapter(CacheConfig())
        result = cache.get("nonexistent_key")

        assert result is None

    def test_set_and_get(self):
        """Test setting and getting value."""
        cache = CacheAdapter(CacheConfig())
        cache.set("test_key", {"value": "test"})

        result = cache.get("test_key")

        assert result == {"value": "test"}

    def test_set_with_custom_ttl(self):
        """Test setting value with custom TTL."""
        cache = CacheAdapter(CacheConfig(ttl_seconds=60))
        cache.set("test_key", "value", ttl_seconds=30)

        result = cache.get("test_key")

        assert result == "value"

    def test_delete_key(self):
        """Test deleting key."""
        cache = CacheAdapter(CacheConfig())
        cache.set("test_key", "value")
        cache.delete("test_key")

        result = cache.get("test_key")

        assert result is None

    def test_delete_nonexistent_key(self):
        """Test deleting nonexistent key doesn't raise error."""
        cache = CacheAdapter(CacheConfig())
        cache.delete("nonexistent_key")  # Should not raise

    def test_clear(self):
        """Test clearing all keys."""
        cache = CacheAdapter(CacheConfig())
        cache.set("key1", "value1")
        cache.set("key2", "value2")

        cache.clear()

        assert cache.get("key1") is None
        assert cache.get("key2") is None

    def test_disabled_cache(self):
        """Test that disabled cache doesn't store values."""
        cache = CacheAdapter(CacheConfig(enabled=False))
        cache.set("test_key", "value")

        result = cache.get("test_key")

        assert result is None

    def test_get_stats(self):
        """Test getting cache statistics."""
        cache = CacheAdapter(CacheConfig())
        cache.set("key1", "value1")
        cache.set("key2", "value2")

        stats = cache.get_stats()

        assert stats["enabled"] is True
        assert stats["keys"] == 2
        assert stats["key_prefix"] == "graph_analytics:"

    def test_stats_disabled_cache(self):
        """Test stats for disabled cache."""
        cache = CacheAdapter(CacheConfig(enabled=False))
        stats = cache.get_stats()

        assert stats["enabled"] is False
        assert stats["keys"] == 0


class TestAlgorithmExecutor:
    """Tests for AlgorithmExecutor."""

    def setup_method(self):
        """Set up test fixtures."""
        self.registry = get_registry()
        self.registry.clear()

    def test_execute_algorithm(self):
        """Test executing an algorithm."""
        from apps.graph_engine.backends.networkx_backend import NetworkXBackend

        self.registry.register(MockAlgorithm)
        backend = NetworkXBackend()
        config = AlgorithmConfig(graph_id=uuid4())
        executor = AlgorithmExecutor(backend)

        result = executor.execute("mock_algorithm", config)

        assert isinstance(result, AlgorithmResult)
        assert result.algorithm_name == "mock_algorithm"
        assert result.results == {"node1": 0.5, "node2": 0.8}
        assert result.execution_time_ms >= 0

    def test_execute_with_cache(self):
        """Test executing algorithm with caching."""
        from apps.graph_engine.backends.networkx_backend import NetworkXBackend

        cache = CacheAdapter(CacheConfig())
        self.registry.register(MockAlgorithm)
        backend = NetworkXBackend()
        graph_id = uuid4()
        config = AlgorithmConfig(graph_id=graph_id, use_cache=True)
        executor = AlgorithmExecutor(backend, cache)

        # First execution - cache miss
        result1 = executor.execute("mock_algorithm", config)
        assert result1.cached is False

        # Second execution - cache hit
        result2 = executor.execute("mock_algorithm", config)
        assert result2.cached is True
        assert result2.execution_time_ms == result1.execution_time_ms

    def test_execute_without_cache(self):
        """Test executing algorithm without caching."""
        from apps.graph_engine.backends.networkx_backend import NetworkXBackend

        cache = CacheAdapter(CacheConfig())
        self.registry.register(MockAlgorithm)
        backend = NetworkXBackend()
        graph_id = uuid4()
        config = AlgorithmConfig(graph_id=graph_id, use_cache=False)
        executor = AlgorithmExecutor(backend, cache)

        result1 = executor.execute("mock_algorithm", config)
        result2 = executor.execute("mock_algorithm", config)

        assert result1.cached is False
        assert result2.cached is False

    def test_execute_nonexistent_algorithm(self):
        """Test executing nonexistent algorithm raises error."""
        from apps.graph_engine.backends.networkx_backend import NetworkXBackend

        backend = NetworkXBackend()
        config = AlgorithmConfig(graph_id=uuid4())
        executor = AlgorithmExecutor(backend)

        with pytest.raises(AlgorithmNotFoundError):
            executor.execute("nonexistent", config)

    def test_execute_with_invalid_config(self):
        """Test executing with invalid config raises error."""
        from apps.graph_engine.backends.networkx_backend import NetworkXBackend

        self.registry.register(MockAlgorithm)
        backend = NetworkXBackend()
        config = AlgorithmConfig(graph_id=None)  # Invalid
        executor = AlgorithmExecutor(backend)

        with pytest.raises(InvalidConfigError):
            executor.execute("mock_algorithm", config)

    def test_execute_failing_algorithm(self):
        """Test executing failing algorithm raises execution error."""
        from apps.graph_engine.backends.networkx_backend import NetworkXBackend

        self.registry.register(FailingAlgorithm)
        backend = NetworkXBackend()
        config = AlgorithmConfig(graph_id=uuid4())
        executor = AlgorithmExecutor(backend)

        with pytest.raises(AlgorithmExecutionError, match="Simulated failure"):
            executor.execute("failing_algorithm", config)

    def test_invalidate_graph(self):
        """Test invalidating cached results for a graph."""
        from apps.graph_engine.backends.networkx_backend import NetworkXBackend

        cache = CacheAdapter(CacheConfig())
        self.registry.register(MockAlgorithm)
        backend = NetworkXBackend()
        graph_id = uuid4()
        config = AlgorithmConfig(graph_id=graph_id, use_cache=True)
        executor = AlgorithmExecutor(backend, cache)

        # Execute and cache result
        executor.execute("mock_algorithm", config)

        # Invalidate
        executor.invalidate_graph(graph_id)

        # Should get cache miss now
        result = executor.execute("mock_algorithm", config)
        assert result.cached is False


class TestInMemoryRepository:
    """Tests for InMemoryAnalyticsRepository."""

    def test_save_and_get_result(self):
        """Test saving and retrieving result."""
        from apps.graph_engine.analytics.repositories import (
            InMemoryAnalyticsRepository,
        )

        repo = InMemoryAnalyticsRepository()
        result = AlgorithmResult(
            algorithm_name="test_algo",
            graph_id=uuid4(),
            execution_time_ms=100,
            results={"test": "data"},
        )

        result_id = repo.save_result(result)
        retrieved = repo.get_result(result_id)

        assert result_id is not None
        assert retrieved.algorithm_name == "test_algo"
        assert retrieved.results == {"test": "data"}

    def test_get_nonexistent_result(self):
        """Test getting nonexistent result returns None."""
        from apps.graph_engine.analytics.repositories import (
            InMemoryAnalyticsRepository,
        )

        repo = InMemoryAnalyticsRepository()
        result = repo.get_result("nonexistent_id")

        assert result is None

    def test_get_latest_result(self):
        """Test getting latest result for graph and algorithm."""
        from datetime import timedelta

        from apps.graph_engine.analytics.repositories import (
            InMemoryAnalyticsRepository,
        )

        repo = InMemoryAnalyticsRepository()
        graph_id = uuid4()

        result1 = AlgorithmResult(
            algorithm_name="test_algo",
            graph_id=graph_id,
            execution_time_ms=100,
            results={"version": 1},
            metadata={"created_at": datetime.utcnow()},
        )
        result2 = AlgorithmResult(
            algorithm_name="test_algo",
            graph_id=graph_id,
            execution_time_ms=100,
            results={"version": 2},
            metadata={"created_at": datetime.utcnow() + timedelta(seconds=1)},
        )

        repo.save_result(result1)
        repo.save_result(result2)

        latest = repo.get_latest_result(graph_id, "test_algo")

        assert latest is not None
        assert latest.results["version"] == 2

    def test_get_results_by_date_range(self):
        """Test getting results within date range."""
        from datetime import timedelta

        from apps.graph_engine.analytics.repositories import (
            InMemoryAnalyticsRepository,
        )

        repo = InMemoryAnalyticsRepository()
        graph_id = uuid4()
        now = datetime.utcnow()

        old_result = AlgorithmResult(
            algorithm_name="test_algo",
            graph_id=graph_id,
            execution_time_ms=100,
            results={"old": True},
            metadata={"created_at": now - timedelta(days=10)},
        )
        recent_result = AlgorithmResult(
            algorithm_name="test_algo",
            graph_id=graph_id,
            execution_time_ms=100,
            results={"recent": True},
            metadata={"created_at": now - timedelta(days=1)},
        )

        repo.save_result(old_result)
        repo.save_result(recent_result)

        results = repo.get_results_by_date_range(graph_id, now - timedelta(days=2), now)

        assert len(results) == 1
        assert results[0].results["recent"] is True

    def test_delete_old_results(self):
        """Test deleting old results."""
        from datetime import timedelta

        from apps.graph_engine.analytics.repositories import (
            InMemoryAnalyticsRepository,
        )

        repo = InMemoryAnalyticsRepository()
        now = datetime.utcnow()

        old_result = AlgorithmResult(
            algorithm_name="test_algo",
            graph_id=uuid4(),
            execution_time_ms=100,
            results={"old": True},
            metadata={"created_at": now - timedelta(days=10)},
        )
        new_result = AlgorithmResult(
            algorithm_name="test_algo",
            graph_id=uuid4(),
            execution_time_ms=100,
            results={"new": True},
            metadata={"created_at": now - timedelta(days=1)},
        )

        repo.save_result(old_result)
        repo.save_result(new_result)

        deleted = repo.delete_old_results(now - timedelta(days=5))

        assert deleted == 1
        assert repo.get_result_by_date_range is not None

    def test_clear_repository(self):
        """Test clearing all results."""
        from apps.graph_engine.analytics.repositories import (
            InMemoryAnalyticsRepository,
        )

        repo = InMemoryAnalyticsRepository()
        result = AlgorithmResult(
            algorithm_name="test_algo", graph_id=uuid4(), execution_time_ms=100, results={}
        )

        repo.save_result(result)
        repo.clear()

        stats = repo.get_statistics()
        assert stats["total_results"] == 0

    def test_get_statistics(self):
        """Test getting repository statistics."""
        from apps.graph_engine.analytics.repositories import (
            InMemoryAnalyticsRepository,
        )

        repo = InMemoryAnalyticsRepository()
        graph_id = uuid4()

        result1 = AlgorithmResult(
            algorithm_name="algo1", graph_id=graph_id, execution_time_ms=100, results={}
        )
        result2 = AlgorithmResult(
            algorithm_name="algo2", graph_id=uuid4(), execution_time_ms=100, results={}
        )

        repo.save_result(result1)
        repo.save_result(result2)

        stats = repo.get_statistics()

        assert stats["total_results"] == 2
        assert stats["graphs_stored"] == 2
        assert stats["algorithms_stored"] == 2
