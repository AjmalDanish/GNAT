"""
Unit Tests for GraphMetrics Service.

Status: Phase 2 - Graph Construction Engine
"""

import pytest

from apps.graph_engine.backends.networkx_backend import NetworkXBackend
from apps.graph_engine.services.graph_metrics import GraphMetrics


@pytest.mark.django_db
class TestGraphMetrics:
    """Tests for GraphMetrics service."""

    def test_initialization(self):
        """Test initialization with backend."""
        backend = NetworkXBackend()
        metrics = GraphMetrics(backend)
        assert metrics.backend is backend

    def test_calculate_degree_metrics_empty_graph(self):
        """Test degree metrics on empty graph."""
        backend = NetworkXBackend()
        metrics = GraphMetrics(backend)
        result = metrics.calculate_degree_metrics()
        assert result == {}

    def test_calculate_degree_metrics(self):
        """Test degree metrics calculation."""
        backend = NetworkXBackend()
        backend.add_node(node_id="city1")
        backend.add_node(node_id="city2")
        backend.add_node(node_id="city3")
        backend.add_edge(source_id="city1", target_id="city2")
        backend.add_edge(source_id="city2", target_id="city3")
        backend.add_edge(source_id="city1", target_id="city3")

        metrics = GraphMetrics(backend)
        result = metrics.calculate_degree_metrics()

        assert "city1" in result
        assert result["city1"]["degree"] == 2
        assert result["city1"]["out_degree"] == 2
        assert result["city1"]["in_degree"] == 0

        assert "city2" in result
        assert result["city2"]["degree"] == 2
        assert result["city2"]["out_degree"] == 1
        assert result["city2"]["in_degree"] == 1

    def test_calculate_centrality_metrics(self):
        """Test centrality metrics calculation."""
        backend = NetworkXBackend()
        backend.add_node(node_id="city1")
        backend.add_node(node_id="city2")
        backend.add_node(node_id="city3")
        backend.add_edge(source_id="city1", target_id="city2")
        backend.add_edge(source_id="city2", target_id="city3")

        metrics = GraphMetrics(backend)
        result = metrics.calculate_centrality_metrics()

        assert "city1" in result
        assert "city2" in result
        assert "city3" in result
        assert "betweenness" in result["city2"]
        assert "closeness" in result["city2"]

    def test_calculate_connectivity_metrics_empty(self):
        """Test connectivity metrics on empty graph."""
        backend = NetworkXBackend()
        metrics = GraphMetrics(backend)
        result = metrics.calculate_connectivity_metrics()

        assert result["node_count"] == 0
        assert result["edge_count"] == 0
        assert result["connected_components"] == 0
        assert result["density"] == 0.0

    def test_calculate_connectivity_metrics(self):
        """Test connectivity metrics calculation."""
        backend = NetworkXBackend()
        backend.add_node(node_id="city1")
        backend.add_node(node_id="city2")
        backend.add_edge(source_id="city1", target_id="city2")

        metrics = GraphMetrics(backend)
        result = metrics.calculate_connectivity_metrics()

        assert result["node_count"] == 2
        assert result["edge_count"] == 1
        assert result["connected_components"] == 1
        assert 0 < result["density"] <= 1.0

    def test_find_shortest_path_single(self):
        """Test finding a single shortest path."""
        backend = NetworkXBackend()
        backend.add_node(node_id="city1")
        backend.add_node(node_id="city2")
        backend.add_node(node_id="city3")
        backend.add_edge(source_id="city1", target_id="city2", latency=100)
        backend.add_edge(source_id="city2", target_id="city3", latency=50)

        metrics = GraphMetrics(backend)
        result = metrics.find_shortest_paths(source_id="city1", target_id="city3")

        assert ("city1", "city3") in result
        assert result[("city1", "city3")] == ["city1", "city2", "city3"]

    def test_find_shortest_path_all_pairs(self):
        """Test finding all pairs shortest paths."""
        backend = NetworkXBackend()
        backend.add_node(node_id="city1")
        backend.add_node(node_id="city2")
        backend.add_edge(source_id="city1", target_id="city2")

        metrics = GraphMetrics(backend)
        result = metrics.find_shortest_paths()

        assert ("city1", "city2") in result
        assert ("city2", "city1") in result

    def test_get_node_summary(self):
        """Test getting node summary."""
        backend = NetworkXBackend()
        backend.add_node(
            node_id="city1",
            country="USA",
            city="New York",
            coordinates=(40.7128, -74.0060),
        )
        backend.add_edge(source_id="city1", target_id="city2", bandwidth=1000.0)
        backend.add_node(node_id="city2")
        backend.add_edge(source_id="city2", target_id="city1")

        metrics = GraphMetrics(backend)
        summary = metrics.get_node_summary("city1")

        assert summary["id"] == "city1"
        assert summary["attributes"]["country"] == "USA"
        assert summary["attributes"]["city"] == "New York"
        assert summary["degree"] == 2
        assert summary["in_degree"] == 1
        assert summary["out_degree"] == 1

    def test_get_edge_summary(self):
        """Test getting edge summary."""
        backend = NetworkXBackend()
        backend.add_node(node_id="city1")
        backend.add_node(node_id="city2")
        backend.add_edge(
            source_id="city1",
            target_id="city2",
            bandwidth=1000.0,
            latency=100.5,
        )

        metrics = GraphMetrics(backend)
        summary = metrics.get_edge_summary("city1", "city2")

        assert summary["source"] == "city1"
        assert summary["target"] == "city2"
        assert summary["attributes"]["bandwidth"] == 1000.0
        assert summary["attributes"]["latency"] == 100.5

    def test_get_edge_summary_nonexistent(self):
        """Test getting summary for nonexistent edge."""
        backend = NetworkXBackend()
        backend.add_node(node_id="city1")
        backend.add_node(node_id="city2")

        metrics = GraphMetrics(backend)
        summary = metrics.get_edge_summary("city1", "city2")

        assert summary == {}

    def test_get_graph_summary(self):
        """Test getting comprehensive graph summary."""
        backend = NetworkXBackend()
        backend.add_node(node_id="city1")
        backend.add_node(node_id="city2")
        backend.add_edge(source_id="city1", target_id="city2")

        metrics = GraphMetrics(backend)
        summary = metrics.get_graph_summary()

        assert "nodes" in summary
        assert "edges" in summary
        assert "connectivity" in summary
        assert "degree_metrics" in summary
        assert "centrality_metrics" in summary
        assert summary["nodes"] == 2
        assert summary["edges"] == 1
