"""
Additional Unit Tests for GraphMetrics Service - Coverage Extension.

Status: Phase 2 - Graph Construction Engine - Coverage >90%
"""

from apps.graph_engine.backends.networkx_backend import NetworkXBackend
from apps.graph_engine.services.graph_metrics import GraphMetrics


class TestGraphMetricsCoverage:
    """Additional coverage tests for GraphMetrics."""

    def test_degree_metrics_single_node_no_edges(self):
        """Test degree metrics on single node with no edges."""
        backend = NetworkXBackend()
        backend.add_node(node_id="city1", city="New York")

        metrics = GraphMetrics(backend)
        result = metrics.calculate_degree_metrics()

        assert result["city1"]["degree"] == 0
        assert result["city1"]["in_degree"] == 0
        assert result["city1"]["out_degree"] == 0

    def test_degree_metrics_bidirectional_edge(self):
        """Test degree metrics with bidirectional edge."""
        backend = NetworkXBackend()
        backend.add_node(node_id="city1")
        backend.add_node(node_id="city2")
        backend.add_edge(source_id="city1", target_id="city2", bandwidth=1000)
        backend.add_edge(source_id="city2", target_id="city1", bandwidth=2000)

        metrics = GraphMetrics(backend)
        result = metrics.calculate_degree_metrics()

        assert result["city1"]["in_degree"] == 1
        assert result["city1"]["out_degree"] == 1
        assert result["city1"]["degree"] == 2
        assert result["city2"]["in_degree"] == 1
        assert result["city2"]["out_degree"] == 1
        assert result["city2"]["degree"] == 2

    def test_centrality_metrics_empty_graph(self):
        """Test centrality metrics on empty graph."""
        backend = NetworkXBackend()
        metrics = GraphMetrics(backend)
        result = metrics.calculate_centrality_metrics()
        assert result == {}

    def test_centrality_metrics_single_node(self):
        """Test centrality metrics on single node."""
        backend = NetworkXBackend()
        backend.add_node(node_id="city1")

        metrics = GraphMetrics(backend)
        result = metrics.calculate_centrality_metrics()

        assert "city1" in result

    def test_centrality_metrics_two_nodes_no_path(self):
        """Test centrality metrics on two disconnected nodes."""
        backend = NetworkXBackend()
        backend.add_node(node_id="city1")
        backend.add_node(node_id="city2")

        metrics = GraphMetrics(backend)
        result = metrics.calculate_centrality_metrics()

        assert "city1" in result
        assert "city2" in result

    def test_connectivity_metrics_empty_graph(self):
        """Test connectivity metrics on empty graph."""
        backend = NetworkXBackend()
        metrics = GraphMetrics(backend)
        result = metrics.calculate_connectivity_metrics()

        assert result["node_count"] == 0
        assert result["edge_count"] == 0
        assert result["connected_components"] == 0
        assert result["largest_component_size"] == 0
        assert result["density"] == 0.0

    def test_connectivity_metrics_single_node(self):
        """Test connectivity metrics on single node."""
        backend = NetworkXBackend()
        backend.add_node(node_id="city1")

        metrics = GraphMetrics(backend)
        result = metrics.calculate_connectivity_metrics()

        assert result["node_count"] == 1
        assert result["edge_count"] == 0
        assert result["connected_components"] == 1
        assert result["largest_component_size"] == 1

    def test_find_shortest_paths_empty_graph(self):
        """Test shortest paths on empty graph."""
        backend = NetworkXBackend()
        metrics = GraphMetrics(backend)
        result = metrics.find_shortest_paths()
        assert result == {}

    def test_find_shortest_paths_source_only(self):
        """Test shortest paths with only source specified."""
        backend = NetworkXBackend()
        backend.add_node(node_id="city1")
        backend.add_node(node_id="city2")
        backend.add_edge(source_id="city1", target_id="city2")

        metrics = GraphMetrics(backend)
        result = metrics.find_shortest_paths(source_id="city1")

        assert ("city1", "city2") in result

    def test_find_shortest_paths_weighted_vs_unweighted(self):
        """Test difference between weighted and unweighted shortest paths."""
        backend = NetworkXBackend()
        backend.add_node(node_id="city1")
        backend.add_node(node_id="city2")
        backend.add_node(node_id="city3")
        backend.add_edge(source_id="city1", target_id="city2", latency=10)
        backend.add_edge(source_id="city1", target_id="city3", latency=1)
        backend.add_edge(source_id="city3", target_id="city2", latency=1)

        metrics = GraphMetrics(backend)

        # Unweighted (hop count)
        unweighted = metrics.find_shortest_paths(source_id="city1", target_id="city2", weight=None)

        # Weighted (latency)
        weighted = metrics.find_shortest_paths(
            source_id="city1", target_id="city2", weight="latency"
        )

        # Both should return paths
        assert unweighted[("city1", "city2")] is not None
        assert weighted[("city1", "city2")] is not None

    def test_get_node_summary_with_attributes(self):
        """Test node summary includes all attributes."""
        backend = NetworkXBackend()
        backend.add_node(
            node_id="city1",
            country="USA",
            city="New York",
            coordinates=(40.7128, -74.0060),
            population=8400000,
        )

        metrics = GraphMetrics(backend)
        summary = metrics.get_node_summary("city1")

        assert summary["id"] == "city1"
        assert summary["attributes"]["country"] == "USA"
        assert summary["attributes"]["city"] == "New York"
        assert summary["attributes"]["coordinates"] == (40.7128, -74.0060)
        assert summary["attributes"]["population"] == 8400000

    def test_get_edge_summary_no_edge(self):
        """Test edge summary when no edge exists."""
        backend = NetworkXBackend()
        backend.add_node(node_id="city1")
        backend.add_node(node_id="city2")

        metrics = GraphMetrics(backend)
        summary = metrics.get_edge_summary("city1", "city2")

        assert summary == {}

    def test_get_graph_summary_complete_with_attributes(self):
        """Test complete graph summary with all metrics."""
        backend = NetworkXBackend()
        backend.add_node(
            node_id="city1",
            country="USA",
            city="New York",
            coordinates=(40.7128, -74.0060),
        )
        backend.add_node(
            node_id="city2",
            country="USA",
            city="Los Angeles",
            coordinates=(34.0522, -118.2437),
        )
        backend.add_edge(
            source_id="city1",
            target_id="city2",
            bandwidth=1000.0,
            latency=100.5,
            protocol="TCP",
        )

        metrics = GraphMetrics(backend)
        summary = metrics.get_graph_summary()

        assert summary["nodes"] == 2
        assert summary["edges"] == 1
        assert "connectivity" in summary
        assert "degree_metrics" in summary
        assert "centrality_metrics" in summary
        assert "city1" in summary["degree_metrics"]
        assert "city2" in summary["degree_metrics"]
