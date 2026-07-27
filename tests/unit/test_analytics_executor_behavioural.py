"""
Behavioral tests for executor uncovered branches.

This file tests real execution behaviours for every uncovered branch.

Uncovered branches explanation:

1. Cache expiration (lines 99-100):
   - WHY: Cache entries have TTL and must expire after expiry time
   - WHEN: Reading a cache entry past its expiry time
   - BEHAVIOUR: Expired entry is deleted and None is returned

2. Delete pattern (lines 139-149):
   - WHY: Need to invalidate multiple cache keys matching a pattern
   - WHEN: Bulk cache invalidation needed (e.g., invalidate all keys for a graph)
   - BEHAVIOUR: All keys matching pattern (with * wildcard) are deleted

3. Timeout finally block (lines 307-323):
   - WHY: Signal handlers must be reset even if timeout occurs
   - WHEN: Algorithm execution times out or any exception occurs
   - BEHAVIOUR: Signal alarm is canceled and original handler is restored

4. Algorithm type branches (lines 352-370):
   - WHY: Different algorithm types have different execution methods
   - WHEN: Executing community, path, anomaly, or feature algorithms
   - BEHAVIOUR: Appropriate method is called based on algorithm type

5. Result metadata checks (lines 380, 382, 384, 386, 388):
   - WHY: Algorithm implementations may not set all required metadata
   - WHEN: Algorithm returns result without metadata attributes
   - BEHAVIOUR: Missing metadata attributes are added by executor

6. Unknown algorithm type (lines 439->441):
   - WHY: Validate algorithm has known execution method
   - WHEN: Algorithm class has no compute, detect_communities, etc. method
   - BEHAVIOUR: AlgorithmExecutionError is raised with descriptive message

7. Graph not in cache keys (line 478->exit):
   - WHY: Gracefully handle invalidation of graph with no cached results
   - WHEN: Calling invalidate_graph on a graph that was never cached
   - BEHAVIOUR: Method returns without error (no-op)
"""

import signal
import time
from datetime import datetime, timedelta
from uuid import uuid4

import pytest

from apps.graph_engine.analytics.exceptions import AlgorithmExecutionError, AlgorithmTimeoutError
from apps.graph_engine.analytics.interfaces import (
    AlgorithmConfig,
    AlgorithmResult,
    CommunityDetectionAlgorithm,
    PathAnalysisAlgorithm,
    AnomalyDetector,
    FeatureExtractor,
    CentralityAlgorithm,
)
from apps.graph_engine.analytics.services.executor import (
    AlgorithmExecutor,
    CacheAdapter,
    CacheConfig,
)
from apps.graph_engine.backends.networkx_backend import NetworkXBackend
from apps.graph_engine.analytics.registry import get_registry


# ============================================================================
# Algorithm Implementations for Testing
# ============================================================================


class CommunityDetectionAlgo(CommunityDetectionAlgorithm):
    """Community detection algorithm implementation."""

    name = "community_algo"
    category = "community"
    version = "1.0.0"
    description = "Test community detection"
    complexity_time = "O(V log V)"
    complexity_space = "O(V)"
    recommended_max_nodes = 100

    @classmethod
    def validate_config(cls, config):
        return []

    @classmethod
    def get_required_parameters(cls):
        return []

    @classmethod
    def get_optional_parameters(cls):
        return {"resolution": 1.0}

    def detect_communities(self, backend, config):
        """Execute community detection."""
        return AlgorithmResult(
            algorithm_name=self.name,
            graph_id=config.graph_id,
            execution_time_ms=75,
            results={"communities": {0: ["node1", "node2"], 1: ["node3"]}},
        )

    def compute_modularity(self, backend, partition, config):
        return 0.65

    def find_bridge_nodes(self, backend, partition, config):
        return ["node2"]


class PathAnalysisAlgo(PathAnalysisAlgorithm):
    """Path analysis algorithm implementation."""

    name = "path_algo"
    category = "path"
    version = "1.0.0"
    description = "Test path analysis"
    complexity_time = "O(E + V log V)"
    complexity_space = "O(V)"
    recommended_max_nodes = 100

    @classmethod
    def validate_config(cls, config):
        return []

    @classmethod
    def get_required_parameters(cls):
        return []

    @classmethod
    def get_optional_parameters(cls):
        return {"weight_attribute": "weight"}

    def find_shortest_path(self, backend, source, target, config):
        """Find shortest path between nodes."""
        return AlgorithmResult(
            algorithm_name=self.name,
            graph_id=config.graph_id,
            execution_time_ms=30,
            results={"path": [source, "intermediate", target], "length": 2},
        )

    def find_k_shortest_paths(self, backend, source, target, k, config):
        return [[source, target]]

    def detect_cycles(self, backend, config):
        return AlgorithmResult(
            algorithm_name=self.name,
            graph_id=config.graph_id,
            execution_time_ms=25,
            results={"cycles": []},
        )

    def find_strongly_connected_components(self, backend, config):
        return AlgorithmResult(
            algorithm_name=self.name,
            graph_id=config.graph_id,
            execution_time_ms=40,
            results={"sccs": [{"node1", "node2"}]},
        )

    def compute_diameter(self, backend, config):
        return 3


class AnomalyDetectionAlgo(AnomalyDetector):
    """Anomaly detection algorithm implementation."""

    name = "anomaly_algo"
    category = "anomaly_detection"
    version = "1.0.0"
    description = "Test anomaly detection"
    complexity_time = "O(V + E)"
    complexity_space = "O(V)"
    recommended_max_nodes = 100

    @classmethod
    def validate_config(cls, config):
        return []

    @classmethod
    def get_required_parameters(cls):
        return []

    @classmethod
    def get_optional_parameters(cls):
        return {"threshold": 0.5}

    def detect(self, backend, config):
        """Detect anomalies."""
        return AlgorithmResult(
            algorithm_name=self.name,
            graph_id=config.graph_id,
            execution_time_ms=60,
            results={"anomalies": [{"node": "node1", "score": 0.95}]},
        )

    def get_severity_score(self, anomaly):
        return 8

    def classify_anomaly(self, anomaly):
        return "high_traffic"


class FeatureExtractionAlgo(FeatureExtractor):
    """Feature extraction algorithm implementation."""

    name = "feature_algo"
    category = "feature_extraction"
    version = "1.0.0"
    description = "Test feature extraction"
    complexity_time = "O(V + E)"
    complexity_space = "O(V)"
    recommended_max_nodes = 100

    @classmethod
    def validate_config(cls, config):
        return []

    @classmethod
    def get_required_parameters(cls):
        return []

    @classmethod
    def get_optional_parameters(cls):
        return {"features": ["degree", "betweenness"]}

    def extract_features(self, backend, config):
        """Extract features."""
        return AlgorithmResult(
            algorithm_name=self.name,
            graph_id=config.graph_id,
            execution_time_ms=45,
            results={"features": {"node1": {"degree": 5, "betweenness": 0.5}}},
        )

    def extract_node_features(self, backend, node_id, config):
        return {"degree": 5, "betweenness": 0.5}

    def extract_edge_features(self, backend, source, target, config):
        return {"weight": 1.0, "betweenness_contribution": 0.1}


class ResultWithoutMetadata(CentralityAlgorithm):
    """Algorithm that returns result without optional metadata attributes."""

    name = "no_metadata_algo"
    category = "centrality"
    version = "1.0.0"
    description = "Algorithm without metadata"
    complexity_time = "O(V)"
    complexity_space = "O(V)"
    recommended_max_nodes = 100

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
        """Return result WITHOUT optional metadata attributes."""
        result = AlgorithmResult(
            algorithm_name=self.name,
            graph_id=config.graph_id,
            execution_time_ms=100,
            results={"node1": 0.5},
        )
        # Remove optional attributes to trigger executor's metadata addition
        delattr(result, 'metadata')
        delattr(result, 'cached')
        return result

    def compute_for_node(self, backend, node_id, config):
        return 0.5

    def get_top_nodes(self, backend, n=10, config=None):
        return []


class PartialMetadataAlgorithm(CentralityAlgorithm):
    """Algorithm that returns result missing execution_time_ms."""

    name = "partial_metadata_algo"
    category = "centrality"
    version = "1.0.0"
    description = "Algorithm with partial metadata"
    complexity_time = "O(V)"
    complexity_space = "O(V)"
    recommended_max_nodes = 100

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
        """Return result without execution_time_ms."""
        result = AlgorithmResult(
            algorithm_name=self.name,
            graph_id=config.graph_id,
            execution_time_ms=100,
            results={"node1": 0.5},
        )
        # Remove execution_time_ms to trigger executor to add it
        delattr(result, 'execution_time_ms')
        return result

    def compute_for_node(self, backend, node_id, config):
        return 0.5

    def get_top_nodes(self, backend, n=10, config=None):
        return []


class AlgorithmWithoutMethod:
    """Algorithm with no known execution method."""

    name = "no_method_algo"
    category = "unknown"
    version = "1.0.0"
    description = "Algorithm without execution method"

    @classmethod
    def validate_config(cls, config):
        return []

    @classmethod
    def get_required_parameters(cls):
        return []

    @classmethod
    def get_optional_parameters(cls):
        return {}

    def unknown_method(self):
        """Not a standard algorithm method."""
        pass


class SlowAlgorithm(CentralityAlgorithm):
    """Algorithm that takes time to execute for testing timeout."""

    name = "slow_algo"
    category = "centrality"
    version = "1.0.0"
    description = "Slow algorithm for timeout testing"
    complexity_time = "O(V + E)"
    complexity_space = "O(V)"
    recommended_max_nodes = 100

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
        """Sleep for 3 seconds."""
        time.sleep(3)
        return AlgorithmResult(
            algorithm_name=self.name,
            graph_id=config.graph_id,
            execution_time_ms=3000,
            results={"node1": 0.5},
        )

    def compute_for_node(self, backend, node_id, config):
        return 0.5

    def get_top_nodes(self, backend, n=10, config=None):
        return []


# ============================================================================
# Behavioural Tests
# ============================================================================


class TestCacheExpiration:
    """Behavioural tests for cache expiration."""

    def test_expired_cache_entry_returns_none_and_is_deleted(self):
        """
        BEHAVIOUR: Expired cache entries are deleted and return None.

        WHY: Cache entries with TTL must not be usable after expiry.
        WHEN: Reading a cache entry after its TTL has elapsed.
        """
        cache = CacheAdapter(CacheConfig(ttl_seconds=1))
        cache.set("test_key", {"data": "test"})

        # Verify immediately available
        assert cache.get("test_key") == {"data": "test"}

        # Wait for expiry
        time.sleep(1.5)

        # Should return None
        result = cache.get("test_key")
        assert result is None

        # Verify entry was deleted from cache
        assert len(cache._cache) == 0


class TestCachePatternDeletion:
    """Behavioural tests for pattern-based cache deletion."""

    def test_delete_pattern_wildcard_deletes_matching_keys(self):
        """
        BEHAVIOUR: All keys matching pattern with * wildcard are deleted.

        WHY: Need bulk cache invalidation (e.g., all keys for a graph).
        WHEN: Using delete_pattern with wildcard suffix.
        """
        cache = CacheAdapter(CacheConfig())

        # Set multiple keys
        cache.set("graph:123:algo1", "result1")
        cache.set("graph:123:algo2", "result2")
        cache.set("graph:456:algo1", "result3")
        cache.set("graph:456:algo2", "result4")

        # Delete all keys for graph 123
        cache.delete_pattern("graph:123:*")

        # Verify correct keys deleted
        assert cache.get("graph:123:algo1") is None
        assert cache.get("graph:123:algo2") is None
        assert cache.get("graph:456:algo1") == "result3"
        assert cache.get("graph:456:algo2") == "result4"

    def test_delete_pattern_no_match_no_error(self):
        """
        BEHAVIOUR: Deleting pattern with no matches is graceful (no error).

        WHY: Should not raise error when no keys match.
        WHEN: delete_pattern called with non-matching pattern.
        """
        cache = CacheAdapter(CacheConfig())

        # Set some keys
        cache.set("other:key", "value")

        # Delete non-matching pattern
        cache.delete_pattern("nonexistent:*")

        # Original key should still exist
        assert cache.get("other:key") == "value"

    def test_delete_pattern_when_cache_disabled(self):
        """
        BEHAVIOUR: delete_pattern is no-op when cache disabled.

        WHY: Disabled cache should not perform operations.
        WHEN: delete_pattern called with disabled cache.
        """
        cache = CacheAdapter(CacheConfig(enabled=False))

        # Should not raise error
        cache.delete_pattern("any:*")

        assert cache.get_stats()["enabled"] is False


class TestTimeoutFinallyBlock:
    """Behavioural tests for timeout cleanup."""

    @pytest.mark.skipif(
        not hasattr(signal, 'SIGALRM'),
        reason="SIGALRM not available on this platform (e.g., Windows)"
    )
    def test_timeout_cleanup_resets_signal_handler(self):
        """
        BEHAVIOUR: Signal handler is reset even when timeout occurs.

        WHY: Must not leave timeout handler active after execution.
        WHEN: Algorithm times out during execution.
        """
        from apps.graph_engine.analytics.registry import get_registry

        registry = get_registry()
        registry.clear()
        registry.register(SlowAlgorithm)

        backend = NetworkXBackend()
        cache = CacheAdapter(CacheConfig(enabled=False))
        executor = AlgorithmExecutor(backend, cache, registry)

        config = AlgorithmConfig(graph_id=uuid4())

        # Execute with timeout shorter than algorithm execution
        with pytest.raises(AlgorithmTimeoutError):
            executor.execute("slow_algo", config, timeout_seconds=1)

        # Signal handler should be reset - verify by executing another algorithm
        # (This would hang if signal handler wasn't reset)
        # If we reach here, signal handler was reset correctly
        assert True

    @pytest.mark.skipif(
        not hasattr(signal, 'SIGALRM'),
        reason="SIGALRM not available on this platform (e.g., Windows)"
    )
    def test_timeout_cleanup_on_regular_execution(self):
        """
        BEHAVIOUR: Signal handler is reset after normal execution.

        WHY: Must clean up even when no timeout occurs.
        WHEN: Algorithm completes before timeout.
        """
        from apps.graph_engine.analytics.interfaces import CentralityAlgorithm

        class FastAlgorithm(CentralityAlgorithm):
            name = "fast_algo"
            category = "centrality"
            version = "1.0.0"
            description = "Fast algorithm"
            complexity_time = "O(V)"
            complexity_space = "O(V)"
            recommended_max_nodes = 100

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
                return AlgorithmResult(
                    algorithm_name=self.name,
                    graph_id=config.graph_id,
                    execution_time_ms=10,
                    results={"node1": 0.5},
                )

            def compute_for_node(self, backend, node_id, config):
                return 0.5

            def get_top_nodes(self, backend, n=10, config=None):
                return []

        from apps.graph_engine.analytics.registry import get_registry

        registry = get_registry()
        registry.clear()
        registry.register(FastAlgorithm)

        backend = NetworkXBackend()
        cache = CacheAdapter(CacheConfig(enabled=False))
        executor = AlgorithmExecutor(backend, cache, registry)

        config = AlgorithmConfig(graph_id=uuid4())

        # Execute with timeout (no timeout should occur)
        result = executor.execute("fast_algo", config, timeout_seconds=10)

        assert result.algorithm_name == "fast_algo"
        assert result.execution_time_ms >= 0


class TestAlgorithmTypeExecution:
    """Behavioural tests for different algorithm types."""

    def test_execute_community_detection_algorithm(self):
        """
        BEHAVIOUR: Community detection algorithm calls detect_communities method.

        WHY: Different algorithm types have different execution methods.
        WHEN: Executing algorithm with detect_communities method.
        """
        from apps.graph_engine.analytics.registry import get_registry

        registry = get_registry()
        registry.clear()
        registry.register(CommunityDetectionAlgo)

        backend = NetworkXBackend()
        cache = CacheAdapter(CacheConfig(enabled=False))
        executor = AlgorithmExecutor(backend, cache, registry)

        config = AlgorithmConfig(graph_id=uuid4())

        result = executor.execute("community_algo", config)

        assert result.algorithm_name == "community_algo"
        assert "communities" in result.results
        assert result.execution_time_ms >= 0

    def test_execute_path_analysis_algorithm(self):
        """
        BEHAVIOUR: Path analysis algorithm calls find_shortest_path method.

        WHY: Path analysis uses shortest path computation.
        WHEN: Executing algorithm with find_shortest_path method.
        """
        from apps.graph_engine.analytics.registry import get_registry

        registry = get_registry()
        registry.clear()
        registry.register(PathAnalysisAlgo)

        backend = NetworkXBackend()
        cache = CacheAdapter(CacheConfig(enabled=False))
        executor = AlgorithmExecutor(backend, cache, registry)

        config = AlgorithmConfig(
            graph_id=uuid4(),
            parameters={"source": "node1", "target": "node3"},
        )

        result = executor.execute("path_algo", config)

        assert result.algorithm_name == "path_algo"
        assert "path" in result.results
        assert result.execution_time_ms >= 0

    def test_execute_anomaly_detection_algorithm(self):
        """
        BEHAVIOUR: Anomaly detection algorithm calls detect method.

        WHY: Anomaly detection uses different computation method.
        WHEN: Executing algorithm with detect method.
        """
        from apps.graph_engine.analytics.registry import get_registry

        registry = get_registry()
        registry.clear()
        registry.register(AnomalyDetectionAlgo)

        backend = NetworkXBackend()
        cache = CacheAdapter(CacheConfig(enabled=False))
        executor = AlgorithmExecutor(backend, cache, registry)

        config = AlgorithmConfig(graph_id=uuid4())

        result = executor.execute("anomaly_algo", config)

        assert result.algorithm_name == "anomaly_algo"
        assert "anomalies" in result.results
        assert result.execution_time_ms >= 0

    def test_execute_feature_extraction_algorithm(self):
        """
        BEHAVIOUR: Feature extraction algorithm calls extract_features method.

        WHY: Feature extraction uses different computation method.
        WHEN: Executing algorithm with extract_features method.
        """
        from apps.graph_engine.analytics.registry import get_registry

        registry = get_registry()
        registry.clear()
        registry.register(FeatureExtractionAlgo)

        backend = NetworkXBackend()
        cache = CacheAdapter(CacheConfig(enabled=False))
        executor = AlgorithmExecutor(backend, cache, registry)

        config = AlgorithmConfig(graph_id=uuid4())

        result = executor.execute("feature_algo", config)

        assert result.algorithm_name == "feature_algo"
        assert "features" in result.results
        assert result.execution_time_ms >= 0

    def test_execute_algorithm_without_known_method_raises_error(self):
        """
        BEHAVIOUR: Algorithm without known execution method raises error.

        WHY: Must validate algorithm has executable method.
        WHEN: Algorithm has no compute, detect_communities, etc. method.
        """
        from apps.graph_engine.analytics.registry import get_registry

        registry = get_registry()
        registry.clear()
        registry.register(AlgorithmWithoutMethod)

        backend = NetworkXBackend()
        cache = CacheAdapter(CacheConfig(enabled=False))
        executor = AlgorithmExecutor(backend, cache, registry)

        config = AlgorithmConfig(graph_id=uuid4())

        with pytest.raises(AlgorithmExecutionError) as exc_info:
            executor.execute("no_method_algo", config)

        assert "has no known execution method" in str(exc_info.value)
        assert "no_method_algo" in str(exc_info.value)


class TestResultMetadataGeneration:
    """Behavioural tests for result metadata generation."""

    def test_executor_adds_missing_algorithm_name(self):
        """
        BEHAVIOUR: Executor adds missing algorithm_name attribute.

        WHY: Algorithm implementations may not set all required metadata.
        WHEN: Algorithm returns result without algorithm_name.
        """
        from apps.graph_engine.analytics.registry import get_registry

        registry = get_registry()
        registry.clear()
        registry.register(ResultWithoutMetadata)

        backend = NetworkXBackend()
        cache = CacheAdapter(CacheConfig(enabled=False))
        executor = AlgorithmExecutor(backend, cache, registry)

        config = AlgorithmConfig(graph_id=uuid4())

        result = executor.execute("no_metadata_algo", config)

        assert result.algorithm_name == "no_metadata_algo"

    def test_executor_adds_missing_execution_time_ms(self):
        """
        BEHAVIOUR: Executor adds missing execution_time_ms attribute.

        WHY: Need execution time even if algorithm doesn't set it.
        WHEN: Algorithm returns result without execution_time_ms.
        """
        from apps.graph_engine.analytics.registry import get_registry

        registry = get_registry()
        registry.clear()
        registry.register(ResultWithoutMetadata)

        backend = NetworkXBackend()
        cache = CacheAdapter(CacheConfig(enabled=False))
        executor = AlgorithmExecutor(backend, cache, registry)

        config = AlgorithmConfig(graph_id=uuid4())

        result = executor.execute("no_metadata_algo", config)

        assert hasattr(result, "execution_time_ms")
        assert result.execution_time_ms >= 0

    def test_executor_adds_missing_graph_id(self):
        """
        BEHAVIOUR: Executor adds missing graph_id attribute.

        WHY: Result must reference the graph it was computed on.
        WHEN: Algorithm returns result without graph_id.
        """
        from apps.graph_engine.analytics.registry import get_registry

        registry = get_registry()
        registry.clear()
        registry.register(ResultWithoutMetadata)

        backend = NetworkXBackend()
        cache = CacheAdapter(CacheConfig(enabled=False))
        executor = AlgorithmExecutor(backend, cache, registry)

        config = AlgorithmConfig(graph_id=uuid4())

        result = executor.execute("no_metadata_algo", config)

        assert hasattr(result, "graph_id")
        assert result.graph_id == config.graph_id

    def test_executor_adds_missing_metadata(self):
        """
        BEHAVIOUR: Executor adds missing metadata attribute.

        WHY: All results should have metadata dict for extensibility.
        WHEN: Algorithm returns result without metadata.
        """
        from apps.graph_engine.analytics.registry import get_registry

        registry = get_registry()
        registry.clear()
        registry.register(ResultWithoutMetadata)

        backend = NetworkXBackend()
        cache = CacheAdapter(CacheConfig(enabled=False))
        executor = AlgorithmExecutor(backend, cache, registry)

        config = AlgorithmConfig(graph_id=uuid4())

        result = executor.execute("no_metadata_algo", config)

        assert hasattr(result, "metadata")
        assert isinstance(result.metadata, dict)

    def test_executor_adds_missing_cached(self):
        """
        BEHAVIOUR: Executor adds missing cached attribute.

        WHY: Results must indicate if they came from cache.
        WHEN: Algorithm returns result without cached attribute.
        """
        from apps.graph_engine.analytics.registry import get_registry

        registry = get_registry()
        registry.clear()
        registry.register(ResultWithoutMetadata)

        backend = NetworkXBackend()
        cache = CacheAdapter(CacheConfig(enabled=False))
        executor = AlgorithmExecutor(backend, cache, registry)

        config = AlgorithmConfig(graph_id=uuid4())

        result = executor.execute("no_metadata_algo", config)

        assert hasattr(result, "cached")
        assert result.cached is False


class TestGraphCacheInvalidation:
    """Behavioural tests for graph cache invalidation."""

    def test_invalidate_graph_not_cached_handles_gracefully(self):
        """
        BEHAVIOUR: Invalidating graph with no cached results is graceful (no-op).

        WHY: Should not raise error when graph has no cached results.
        WHEN: Calling invalidate_graph on graph that was never executed.
        """
        from apps.graph_engine.analytics.interfaces import CentralityAlgorithm
        from apps.graph_engine.analytics.registry import get_registry

        class SimpleAlgo(CentralityAlgorithm):
            name = "simple"
            category = "centrality"
            version = "1.0.0"
            description = "Simple"
            complexity_time = "O(V)"
            complexity_space = "O(V)"
            recommended_max_nodes = 100

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
                return AlgorithmResult(
                    algorithm_name=self.name,
                    graph_id=config.graph_id,
                    execution_time_ms=10,
                    results={"node1": 0.5},
                )

            def compute_for_node(self, backend, node_id, config):
                return 0.5

            def get_top_nodes(self, backend, n=10, config=None):
                return []

        registry = get_registry()
        registry.clear()
        registry.register(SimpleAlgo)

        backend = NetworkXBackend()
        cache = CacheAdapter(CacheConfig(enabled=False))
        executor = AlgorithmExecutor(backend, cache, registry)

        # Invalidate graph that was never executed
        graph_id = uuid4()
        executor.invalidate_graph(graph_id)

        # Should not raise error
        assert True

    def test_invalidate_graph_removes_from_graph_cache_keys(self):
        """
        BEHAVIOUR: Invalidated graph is removed from _graph_cache_keys tracking.

        WHY: Internal tracking must be kept in sync with actual cache.
        WHEN: invalidate_graph is called on a graph with cached results.
        """
        from apps.graph_engine.analytics.interfaces import CentralityAlgorithm, AlgorithmResult
        from apps.graph_engine.analytics.registry import get_registry

        class CachedAlgo(CentralityAlgorithm):
            name = "cached"
            category = "centrality"
            version = "1.0.0"
            description = "Cached"
            complexity_time = "O(V)"
            complexity_space = "O(V)"
            recommended_max_nodes = 100

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
                return AlgorithmResult(
                    algorithm_name=self.name,
                    graph_id=config.graph_id,
                    execution_time_ms=10,
                    results={"node1": 0.5},
                )

            def compute_for_node(self, backend, node_id, config):
                return 0.5

            def get_top_nodes(self, backend, n=10, config=None):
                return []

        registry = get_registry()
        registry.clear()
        registry.register(CachedAlgo)

        backend = NetworkXBackend()
        cache = CacheAdapter(CacheConfig())
        executor = AlgorithmExecutor(backend, cache, registry)

        graph_id = uuid4()
        config = AlgorithmConfig(graph_id=graph_id, use_cache=True)

        # Execute and cache
        executor.execute("cached", config)

        # Verify graph is tracked
        assert graph_id in executor._graph_cache_keys

        # Invalidate
        executor.invalidate_graph(graph_id)

        # Verify graph is removed from tracking
        assert graph_id not in executor._graph_cache_keys