"""
Unit tests for analytics interfaces.

Tests all base interfaces and abstract classes.
"""

from datetime import datetime
from uuid import uuid4

import pytest

from apps.graph_engine.analytics.interfaces import (
    AlgorithmConfig,
    AlgorithmResult,
    AlgorithmStrategy,
    AnomalyDetector,
    CentralityAlgorithm,
    CommunityDetectionAlgorithm,
    FeatureExtractor,
    PathAnalysisAlgorithm,
)
from apps.graph_engine.interfaces.graph_backend import GraphBackend


class TestAlgorithmConfig:
    """Tests for AlgorithmConfig dataclass."""

    def test_default_config(self):
        """Test creating config with default values."""
        graph_id = uuid4()
        config = AlgorithmConfig(graph_id=graph_id)

        assert config.graph_id == graph_id
        assert config.timeout_seconds is None
        assert config.use_cache is True
        assert config.cache_ttl_seconds == 3600
        assert config.parameters == {}
        assert config.node_filter is None
        assert config.edge_filter is None

    def test_config_with_custom_values(self):
        """Test creating config with custom values."""
        graph_id = uuid4()
        config = AlgorithmConfig(
            graph_id=graph_id,
            timeout_seconds=300,
            use_cache=False,
            cache_ttl_seconds=7200,
            parameters={"alpha": 0.85},
            node_filter=lambda x: x.startswith("US-"),
        )

        assert config.timeout_seconds == 300
        assert config.use_cache is False
        assert config.cache_ttl_seconds == 7200
        assert config.parameters == {"alpha": 0.85}
        assert config.node_filter is not None

    def test_config_parameters_dict(self):
        """Test that parameters dict is not shared between instances."""
        config1 = AlgorithmConfig(graph_id=uuid4())
        config2 = AlgorithmConfig(graph_id=uuid4())

        config1.parameters["test"] = "value"

        assert "test" not in config2.parameters


class TestAlgorithmResult:
    """Tests for AlgorithmResult dataclass."""

    def test_result_creation(self):
        """Test creating algorithm result."""
        graph_id = uuid4()
        result = AlgorithmResult(
            algorithm_name="test_algorithm",
            graph_id=graph_id,
            execution_time_ms=1000,
            results={"node1": 0.5, "node2": 0.8},
            metadata={"version": "1.0"},
            cached=False,
        )

        assert result.algorithm_name == "test_algorithm"
        assert result.graph_id == graph_id
        assert result.execution_time_ms == 1000
        assert result.results == {"node1": 0.5, "node2": 0.8}
        assert result.metadata == {"version": "1.0"}
        assert result.cached is False

    def test_result_with_default_metadata(self):
        """Test creating result with default metadata."""
        graph_id = uuid4()
        result = AlgorithmResult(
            algorithm_name="test_algorithm",
            graph_id=graph_id,
            execution_time_ms=500,
            results={"test": "data"},
        )

        assert result.metadata == {}
        assert result.cached is False


class TestAlgorithmStrategy:
    """Tests for AlgorithmStrategy abstract base class."""

    def test_cannot_instantiate_base_class(self):
        """Test that base class cannot be instantiated."""
        with pytest.raises(TypeError):
            AlgorithmStrategy()


class TestConcreteAlgorithmImplementations:
    """Tests that concrete algorithms implement required methods."""

    def test_minimal_centrality_algorithm(self):
        """Test minimal centrality algorithm implementation."""

        class TestCentrality(CentralityAlgorithm):
            name = "test_centrality"
            category = "centrality"
            version = "1.0.0"
            description = "Test centrality algorithm"
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
                return {"weighted": False}

            def compute(self, backend, config):
                return AlgorithmResult(
                    algorithm_name=self.name,
                    graph_id=config.graph_id,
                    execution_time_ms=0,
                    results={"node1": 0.5},
                )

            def compute_for_node(self, backend, node_id, config):
                return 0.5

            def get_top_nodes(self, backend, n=10, config=None):
                return [("node1", 0.5)]

        # Verify attributes
        assert TestCentrality.name == "test_centrality"
        assert TestCentrality.category == "centrality"
        assert TestCentrality.validate_config(AlgorithmConfig(graph_id=uuid4())) == []
        assert TestCentrality.get_required_parameters() == []
        assert TestCentrality.get_optional_parameters() == {"weighted": False}

    def test_minimal_community_detection_algorithm(self):
        """Test minimal community detection implementation."""

        class TestCommunity(CommunityDetectionAlgorithm):
            name = "test_community"
            category = "community"
            version = "1.0.0"
            description = "Test community algorithm"
            complexity_time = "O(V log V)"
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
                return {"resolution": 1.0}

            def detect_communities(self, backend, config):
                return AlgorithmResult(
                    algorithm_name=self.name,
                    graph_id=config.graph_id,
                    execution_time_ms=0,
                    results={"node1": 0, "node2": 0},
                )

            def compute_modularity(self, backend, partition, config):
                return 0.5

            def find_bridge_nodes(self, backend, partition, config):
                return ["node1"]

        # Verify attributes
        assert TestCommunity.name == "test_community"
        assert TestCommunity.category == "community"

        # Test instance methods
        community = TestCommunity()
        assert (
            community.compute_modularity(
                None, {"node1": 0}, AlgorithmConfig(graph_id=uuid4())
            )
            == 0.5
        )
        assert community.find_bridge_nodes(
            None, {"node1": 0}, AlgorithmConfig(graph_id=uuid4())
        ) == ["node1"]

    def test_minimal_path_analysis_algorithm(self):
        """Test minimal path analysis implementation."""

        class TestPath(PathAnalysisAlgorithm):
            name = "test_path"
            category = "path"
            version = "1.0.0"
            description = "Test path algorithm"
            complexity_time = "O(E + V log V)"
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
                return {"weight_attribute": "weight"}

            def find_shortest_path(self, backend, source, target, config):
                return AlgorithmResult(
                    algorithm_name=self.name,
                    graph_id=config.graph_id,
                    execution_time_ms=0,
                    results={"path": [source, target], "length": 1},
                )

            def find_k_shortest_paths(self, backend, source, target, k, config):
                return [[source, target]]

            def detect_cycles(self, backend, config):
                return AlgorithmResult(
                    algorithm_name=self.name,
                    graph_id=config.graph_id,
                    execution_time_ms=0,
                    results={"cycles": []},
                )

            def find_strongly_connected_components(self, backend, config):
                return AlgorithmResult(
                    algorithm_name=self.name,
                    graph_id=config.graph_id,
                    execution_time_ms=0,
                    results={"sccs": [{"node1", "node2"}]},
                )

            def compute_diameter(self, backend, config):
                return 5

        # Verify attributes
        assert TestPath.name == "test_path"
        assert TestPath.category == "path"

        # Test instance methods
        path_algo = TestPath()
        paths = path_algo.find_k_shortest_paths(
            None, "A", "B", 2, AlgorithmConfig(graph_id=uuid4())
        )
        assert paths == [["A", "B"]]
        assert path_algo.compute_diameter(None, AlgorithmConfig(graph_id=uuid4())) == 5

    def test_minimal_anomaly_detector(self):
        """Test minimal anomaly detector implementation."""

        class TestDetector(AnomalyDetector):
            name = "test_detector"
            category = "anomaly_detection"
            version = "1.0.0"
            description = "Test anomaly detector"
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
                return {"threshold": 0.5}

            def detect(self, backend, config):
                return AlgorithmResult(
                    algorithm_name=self.name,
                    graph_id=config.graph_id,
                    execution_time_ms=0,
                    results={"anomalies": []},
                )

            def get_severity_score(self, anomaly):
                return 5

            def classify_anomaly(self, anomaly):
                return "test_type"

        # Verify attributes
        assert TestDetector.name == "test_detector"
        assert TestDetector.category == "anomaly_detection"

        # Test instance methods
        detector = TestDetector()
        assert detector.get_severity_score({}) == 5
        assert detector.classify_anomaly({}) == "test_type"

    def test_minimal_feature_extractor(self):
        """Test minimal feature extractor implementation."""

        class TestExtractor(FeatureExtractor):
            name = "test_extractor"
            category = "feature_extraction"
            version = "1.0.0"
            description = "Test feature extractor"
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
                return {"features": ["degree", "betweenness"]}

            def extract_features(self, backend, config):
                return AlgorithmResult(
                    algorithm_name=self.name,
                    graph_id=config.graph_id,
                    execution_time_ms=0,
                    results={"features": {"node1": [1.0, 0.5]}},
                )

            def extract_node_features(self, backend, node_id, config):
                return {"degree": 5, "betweenness": 0.5}

            def extract_edge_features(self, backend, source, target, config):
                return {"weight": 1.0, "betweenness_contribution": 0.1}

        # Verify attributes
        assert TestExtractor.name == "test_extractor"
        assert TestExtractor.category == "feature_extraction"

        # Test instance methods
        extractor = TestExtractor()
        features = extractor.extract_node_features(
            None, "node1", AlgorithmConfig(graph_id=uuid4())
        )
        assert features == {"degree": 5, "betweenness": 0.5}
        edge_features = extractor.extract_edge_features(
            None, "A", "B", AlgorithmConfig(graph_id=uuid4())
        )
        assert edge_features == {"weight": 1.0, "betweenness_contribution": 0.1}
