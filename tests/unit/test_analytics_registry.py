"""
Unit tests for algorithm registry.

Tests registration, retrieval, and algorithm discovery.
"""

from uuid import uuid4

import pytest

from apps.graph_engine.analytics.interfaces import (
    AlgorithmConfig,
    AlgorithmResult,
    AlgorithmStrategy,
    CentralityAlgorithm,
)
from apps.graph_engine.analytics.registry import (
    AlgorithmRegistry,
    get_registry,
    registry,
)


class MockAlgorithm(CentralityAlgorithm):
    """Mock algorithm for testing."""

    name = "mock_algorithm"
    category = "centrality"
    version = "1.0.0"
    description = "Mock algorithm for testing"
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
            algorithm_name=self.name, graph_id=config.graph_id, execution_time_ms=0, results={}
        )

    def compute_for_node(self, backend, node_id, config):
        return 0.5

    def get_top_nodes(self, backend, n=10, config=None):
        return []


class TestAlgorithmRegistry:
    """Tests for AlgorithmRegistry."""

    def test_singleton(self):
        """Test that registry is a singleton."""
        registry1 = AlgorithmRegistry()
        registry2 = AlgorithmRegistry()

        assert registry1 is registry2

    def test_register_algorithm(self):
        """Test registering an algorithm."""
        test_registry = AlgorithmRegistry()

        test_registry.register(MockAlgorithm)

        assert test_registry.is_registered("mock_algorithm")

    def test_register_algorithm_with_custom_name(self):
        """Test registering algorithm with custom name."""
        test_registry = AlgorithmRegistry()

        test_registry.register(MockAlgorithm, name="custom_name")

        assert test_registry.is_registered("custom_name")
        assert not test_registry.is_registered("mock_algorithm")

    def test_register_duplicate_fails(self):
        """Test that registering duplicate algorithm raises error."""
        test_registry = AlgorithmRegistry()
        test_registry.register(MockAlgorithm)

        with pytest.raises(ValueError, match="already registered"):
            test_registry.register(MockAlgorithm)

    def test_register_algorithm_without_name_fails(self):
        """Test that registering algorithm without name attribute fails."""
        test_registry = AlgorithmRegistry()

        class InvalidAlgorithm:
            """Invalid algorithm without name attribute."""

            pass

        with pytest.raises(ValueError, match="must have a 'name' attribute"):
            test_registry.register(InvalidAlgorithm)

    def test_register_algorithm_without_category_fails(self):
        """Test that registering algorithm without category attribute fails."""
        test_registry = AlgorithmRegistry()

        class InvalidAlgorithm:
            """Invalid algorithm without category attribute."""

            name = "invalid"

        with pytest.raises(ValueError, match="must have a 'category' attribute"):
            test_registry.register(InvalidAlgorithm)

    def test_get_algorithm(self):
        """Test getting algorithm by name."""
        test_registry = AlgorithmRegistry()
        test_registry.register(MockAlgorithm)

        algorithm_class = test_registry.get("mock_algorithm")

        assert algorithm_class is MockAlgorithm

    def test_get_nonexistent_algorithm_fails(self):
        """Test that getting nonexistent algorithm raises error."""
        test_registry = AlgorithmRegistry()

        with pytest.raises(KeyError, match="not found"):
            test_registry.get("nonexistent")

    def test_get_by_category(self):
        """Test getting algorithms by category."""
        test_registry = AlgorithmRegistry()
        test_registry.register(MockAlgorithm)

        algorithms = test_registry.get_by_category("centrality")

        assert "mock_algorithm" in algorithms
        assert algorithms["mock_algorithm"] is MockAlgorithm

    def test_get_by_category_empty(self):
        """Test getting algorithms for non-existent category."""
        test_registry = AlgorithmRegistry()

        algorithms = test_registry.get_by_category("nonexistent")

        assert algorithms == {}

    def test_list_algorithms(self):
        """Test listing all algorithms."""
        test_registry = AlgorithmRegistry()
        test_registry.register(MockAlgorithm)

        algorithms = test_registry.list_algorithms()

        assert "mock_algorithm" in algorithms

    def test_list_algorithms_with_category_filter(self):
        """Test listing algorithms with category filter."""
        test_registry = AlgorithmRegistry()
        test_registry.register(MockAlgorithm)

        algorithms = test_registry.list_algorithms(category="centrality")

        assert "mock_algorithm" in algorithms

        algorithms = test_registry.list_algorithms(category="community")
        assert algorithms == []

    def test_list_categories(self):
        """Test listing all categories."""
        test_registry = AlgorithmRegistry()
        test_registry.register(MockAlgorithm)

        categories = test_registry.list_categories()

        assert "centrality" in categories

    def test_is_registered(self):
        """Test checking if algorithm is registered."""
        test_registry = AlgorithmRegistry()

        assert not test_registry.is_registered("mock_algorithm")

        test_registry.register(MockAlgorithm)

        assert test_registry.is_registered("mock_algorithm")

    def test_unregister(self):
        """Test unregistering an algorithm."""
        test_registry = AlgorithmRegistry()
        test_registry.register(MockAlgorithm)

        test_registry.unregister("mock_algorithm")

        assert not test_registry.is_registered("mock_algorithm")

    def test_unregister_nonexistent_fails(self):
        """Test that unregistering nonexistent algorithm raises error."""
        test_registry = AlgorithmRegistry()

        with pytest.raises(KeyError, match="not found"):
            test_registry.unregister("nonexistent")

    def test_unregister_removes_from_category(self):
        """Test that unregistering removes from category index."""
        test_registry = AlgorithmRegistry()
        test_registry.register(MockAlgorithm)

        test_registry.unregister("mock_algorithm")

        algorithms = test_registry.get_by_category("centrality")
        assert "mock_algorithm" not in algorithms

    def test_clear(self):
        """Test clearing all algorithms."""
        test_registry = AlgorithmRegistry()
        test_registry.register(MockAlgorithm)

        test_registry.clear()

        assert not test_registry.is_registered("mock_algorithm")
        assert test_registry.list_algorithms() == []
        assert test_registry.list_categories() == []

    def test_get_metadata(self):
        """Test getting algorithm metadata."""
        test_registry = AlgorithmRegistry()
        test_registry.register(MockAlgorithm)

        metadata = test_registry.get_metadata("mock_algorithm")

        assert metadata["class_name"] == "MockAlgorithm"
        assert metadata["category"] == "centrality"
        assert metadata["version"] == "1.0.0"
        assert metadata["description"] == "Mock algorithm for testing"
        assert metadata["complexity_time"] == "O(V + E)"
        assert metadata["complexity_space"] == "O(V)"
        assert metadata["recommended_max_nodes"] == 100_000

    def test_get_metadata_nonexistent_fails(self):
        """Test that getting metadata for nonexistent algorithm raises error."""
        test_registry = AlgorithmRegistry()

        with pytest.raises(KeyError, match="not found"):
            test_registry.get_metadata("nonexistent")

    def test_get_statistics(self):
        """Test getting registry statistics."""
        test_registry = AlgorithmRegistry()
        test_registry.register(MockAlgorithm)

        stats = test_registry.get_statistics()

        assert stats["total_algorithms"] == 1
        assert stats["total_categories"] == 1
        assert stats["algorithms_by_category"] == {"centrality": 1}

    def test_register_decorator(self):
        """Test using register decorator."""
        test_registry = AlgorithmRegistry()

        @test_registry.register_decorator("decorated_algorithm")
        class DecoratedAlgorithm(CentralityAlgorithm):
            name = "decorated_algorithm"
            category = "centrality"
            version = "1.0.0"
            description = "Decorated algorithm"

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
                    execution_time_ms=0,
                    results={},
                )

            def compute_for_node(self, backend, node_id, config):
                return 0.5

            def get_top_nodes(self, backend, n=10, config=None):
                return []

        assert test_registry.is_registered("decorated_algorithm")


class TestGlobalRegistry:
    """Tests for global registry instance."""

    def test_get_registry(self):
        """Test getting global registry instance."""
        reg = get_registry()

        assert reg is registry
        assert isinstance(reg, AlgorithmRegistry)

    def test_registry_persists(self):
        """Test that global registry persists across calls."""
        test_registry = AlgorithmRegistry()

        # Don't use global registry for this test
        reg1 = get_registry()
        reg2 = get_registry()

        assert reg1 is reg2


class TestRegistryThreadSafety:
    """Tests for registry thread safety."""

    def test_concurrent_registration(self):
        """Test concurrent registration doesn't cause corruption."""
        import threading

        test_registry = AlgorithmRegistry()

        def register_algorithm(name: str):
            class TestAlg(CentralityAlgorithm):
                name = name
                category = "centrality"
                version = "1.0.0"
                description = f"Test algorithm {name}"

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
                        execution_time_ms=0,
                        results={},
                    )

                def compute_for_node(self, backend, node_id, config):
                    return 0.5

                def get_top_nodes(self, backend, n=10, config=None):
                    return []

            test_registry.register(TestAlg)

        threads = [
            threading.Thread(target=register_algorithm, args=(f"algo_{i}",)) for i in range(10)
        ]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        stats = test_registry.get_statistics()
        assert stats["total_algorithms"] == 10
