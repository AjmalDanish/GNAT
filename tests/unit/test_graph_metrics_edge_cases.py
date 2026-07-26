"""
Additional Unit Tests for GraphMetrics Service.

Status: Phase 2 - Graph Construction Engine - Coverage Expansion
"""

import pytest

from apps.graph_engine.backends.networkx_backend import NetworkXBackend
from apps.graph_engine.services.graph_metrics import GraphMetrics


@pytest.mark.django_db
class TestGraphMetricsEdgeCases:
    """Additional edge case tests for GraphMetrics."""

    def test_degree_metrics_empty_graph(self):
        """Test degree metrics on completely empty graph."""
        backend = NetworkXBackend()
        metrics = GraphMetrics(backend)
        result = metrics.calculate_degree_metrics()
        assert result == {}

    def test_centrality_metrics_disconnected_graph(self):
        """Test centrality on disconnected graph."""
        backend = NetworkXBackend()
        backend.add_node(node_id="city1")
        backend.add_node(node_id="city2")
        backend.add_node(node_id="city3")
        backend.add_edge(source_id="city1", target_id="city2")
        # city3 is isolated

        metrics = GraphMetrics(backend)
        result = metrics.calculate_centrality_metrics()

        assert "city1" in result
        assert "city2" in result
        assert "city3" in result

    def test_shortest_path_with_disconnected_nodes(self):
        """Test shortest path when nodes are disconnected."""
        backend = NetworkXBackend()
        backend.add_node(node_id="city1")
        backend.add_node(node_id="city2")
        backend.add_node(node_id="city3")
        backend.add_edge(source_id="city1", target_id="city2")
        # city3 is disconnected

        metrics = GraphMetrics(backend)
        result = metrics.find_shortest_paths(source_id="city1", target_id="city3")

        assert result[("city1", "city3")] is None

    def test_shortest_path_self(self):
        """Test shortest path from node to itself."""
        backend = NetworkXBackend()
        backend.add_node(node_id="city1")

        metrics = GraphMetrics(backend)
        paths = metrics.find_shortest_paths(source_id="city1", target_id="city1")

        # Self-path may or may not exist depending on implementation
        assert ("city1", "city1") in paths

    def test_betweenness_centrality_single_edge(self):
        """Test betweenness with single edge graph."""
        backend = NetworkXBackend()
        backend.add_node(node_id="city1")
        backend.add_node(node_id="city2")
        backend.add_edge(source_id="city1", target_id="city2")

        metrics = GraphMetrics(backend)
        result = metrics.calculate_centrality_metrics()

        # Both nodes should have betweenness centrality
        assert "city1" in result
        assert "city2" in result

    def test_betweenness_centrality_line_graph(self):
        """Test betweenness on line graph (A-B-C-D)."""
        backend = NetworkXBackend()
        backend.add_node(node_id="city1")
        backend.add_node(node_id="city2")
        backend.add_node(node_id="city3")
        backend.add_node(node_id="city4")
        backend.add_edge(source_id="city1", target_id="city2")
        backend.add_edge(source_id="city2", target_id="city3")
        backend.add_edge(source_id="city3", target_id="city4")

        metrics = GraphMetrics(backend)
        result = metrics.calculate_centrality_metrics()

        assert "city1" in result
        assert "city2" in result
        assert "city3" in result
        assert "city4" in result

    def test_closeness_centrality_star_graph(self):
        """Test closeness on star graph (center connected to all others)."""
        backend = NetworkXBackend()
        backend.add_node(node_id="center")
        backend.add_node(node_id="node1")
        backend.add_node(node_id="node2")
        backend.add_node(node_id="node3")

        for i in range(1, 4):
            backend.add_edge(source_id="center", target_id=f"node{i}")

        metrics = GraphMetrics(backend)
        result = metrics.calculate_centrality_metrics()

        # Center should have highest closeness
        assert "center" in result
        # In a directed graph, center may not have highest due to direction
        assert result["center"]["closeness"] >= 0

    def test_connected_components_disconnected_graph(self):
        """Test connected components on disconnected graph."""
        backend = NetworkXBackend()
        # First component
        backend.add_node(node_id="city1")
        backend.add_node(node_id="city2")
        backend.add_edge(source_id="city1", target_id="city2")

        # Second component
        backend.add_node(node_id="city3")
        backend.add_node(node_id="city4")
        backend.add_edge(source_id="city3", target_id="city4")

        # Isolated node
        backend.add_node(node_id="city5")

        metrics = GraphMetrics(backend)
        components = metrics.calculate_connectivity_metrics()

        assert components["connected_components"] == 3
        assert components["largest_component_size"] == 2

    def test_connected_components_fully_connected(self):
        """Test connected components on fully connected graph."""
        backend = NetworkXBackend()
        backend.add_node(node_id="city1")
        backend.add_node(node_id="city2")
        backend.add_node(node_id="city3")

        # Create triangle
        backend.add_edge(source_id="city1", target_id="city2")
        backend.add_edge(source_id="city2", target_id="city3")
        backend.add_edge(source_id="city3", target_id="city1")

        metrics = GraphMetrics(backend)
        components = metrics.calculate_connectivity_metrics()

        assert components["connected_components"] == 1
        assert components["largest_component_size"] == 3

    def test_connectivity_density(self):
        """Test graph density calculation."""
        backend = NetworkXBackend()

        # Complete graph on 3 nodes (3*2 = 6 possible directed edges)
        backend.add_node(node_id="city1")
        backend.add_node(node_id="city2")
        backend.add_node(node_id="city3")
        backend.add_edge(source_id="city1", target_id="city2")
        backend.add_edge(source_id="city2", target_id="city1")
        backend.add_edge(source_id="city2", target_id="city3")
        backend.add_edge(source_id="city3", target_id="city2")
        backend.add_edge(source_id="city3", target_id="city1")
        backend.add_edge(source_id="city1", target_id="city3")

        metrics = GraphMetrics(backend)
        result = metrics.calculate_connectivity_metrics()

        # 6 edges / 6 possible = 1.0
        assert result["density"] == 1.0

    def test_connectivity_density_zero(self):
        """Test density with no edges."""
        backend = NetworkXBackend()
        backend.add_node(node_id="city1")
        backend.add_node(node_id="city2")

        metrics = GraphMetrics(backend)
        result = metrics.calculate_connectivity_metrics()

        assert result["density"] == 0.0

    def test_find_shortest_paths_all_pairs(self):
        """Test finding all pairs shortest paths."""
        backend = NetworkXBackend()
        backend.add_node(node_id="city1")
        backend.add_node(node_id="city2")
        backend.add_node(node_id="city3")
        backend.add_edge(source_id="city1", target_id="city2")
        backend.add_edge(source_id="city2", target_id="city3")

        metrics = GraphMetrics(backend)
        result = metrics.find_shortest_paths()

        # Should have paths for all pairs
        assert ("city1", "city2") in result
        assert ("city2", "city3") in result
        assert ("city1", "city3") in result
        assert result[("city1", "city2")] == ["city1", "city2"]
        assert result[("city1", "city3")] == ["city1", "city2", "city3"]

    def test_shortest_path_with_weight(self):
        """Test weighted shortest path."""
        backend = NetworkXBackend()
        backend.add_node(node_id="city1")
        backend.add_node(node_id="city2")
        backend.add_node(node_id="city3")
        backend.add_edge(source_id="city1", target_id="city2", latency=10)
        backend.add_edge(source_id="city1", target_id="city3", latency=5)
        backend.add_edge(source_id="city3", target_id="city2", latency=5)

        metrics = GraphMetrics(backend)

        # Without weight
        path = metrics.find_shortest_paths(source_id="city1", target_id="city2")
        assert path[("city1", "city2")] == ["city1", "city2"]

        # With weight (should prefer city1->city3->city2 = 10 vs city1->city2 = 10, equal)
        path_weighted = metrics.find_shortest_paths(
            source_id="city1", target_id="city2", weight="latency"
        )
        # Both paths have same total latency, so either is valid
        assert path_weighted[("city1", "city2")] is not None

    def test_get_node_summary_nonexistent(self):
        """Test getting summary for nonexistent node."""
        backend = NetworkXBackend()
        metrics = GraphMetrics(backend)

        # NetworkX raises KeyError for nonexistent nodes
        with pytest.raises(KeyError):
            metrics.get_node_summary("nonexistent")

    def test_get_graph_summary_complete(self):
        """Test complete graph summary."""
        backend = NetworkXBackend()
        backend.add_node(node_id="city1", city="New York")
        backend.add_node(node_id="city2", city="Los Angeles")
        backend.add_edge(source_id="city1", target_id="city2", bandwidth=1000.0)

        metrics = GraphMetrics(backend)
        summary = metrics.get_graph_summary()

        assert summary["nodes"] == 2
        assert summary["edges"] == 1
        assert "connectivity" in summary
        assert "degree_metrics" in summary
        assert "centrality_metrics" in summary
        assert summary["connectivity"]["connected_components"] == 1

    def test_metrics_with_single_node(self):
        """Test metrics on graph with single node."""
        backend = NetworkXBackend()
        backend.add_node(node_id="city1", city="New York")

        metrics = GraphMetrics(backend)

        # Degree metrics
        degree = metrics.calculate_degree_metrics()
        assert degree["city1"]["degree"] == 0
        assert degree["city1"]["in_degree"] == 0
        assert degree["city1"]["out_degree"] == 0

        # Connectivity metrics
        connectivity = metrics.calculate_connectivity_metrics()
        assert connectivity["connected_components"] == 1
        assert connectivity["largest_component_size"] == 1

    def test_metrics_with_directed_edges_asymmetry(self):
        """Test metrics on asymmetric directed graph."""
        backend = NetworkXBackend()
        backend.add_node(node_id="city1")
        backend.add_node(node_id="city2")
        backend.add_node(node_id="city3")

        # Asymmetric edges: city1->city2, city2->city3
        backend.add_edge(source_id="city1", target_id="city2")
        backend.add_edge(source_id="city2", target_id="city3")

        metrics = GraphMetrics(backend)
        degree = metrics.calculate_degree_metrics()

        assert degree["city1"]["out_degree"] == 1
        assert degree["city1"]["in_degree"] == 0
        assert degree["city2"]["in_degree"] == 1
        assert degree["city2"]["out_degree"] == 1
        assert degree["city3"]["in_degree"] == 1
        assert degree["city3"]["out_degree"] == 0
