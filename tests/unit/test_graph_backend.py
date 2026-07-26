"""
Unit Tests for Graph Backend Interface.

This module tests the graph backend interface.

Status: Phase 2 - Graph Construction Engine
"""

from apps.graph_engine.backends.networkx_backend import NetworkXBackend
from apps.graph_engine.interfaces.graph_backend import GraphBackend


class TestGraphBackendInterface:
    """Tests for GraphBackend interface compliance."""

    def test_networkx_backend_implements_interface(self):
        """Test that NetworkXBackend implements GraphBackend."""
        backend = NetworkXBackend()
        assert isinstance(backend, GraphBackend)

    def test_add_and_retrieve_nodes(self):
        """Test adding and retrieving nodes."""
        backend = NetworkXBackend()
        backend.add_node(
            node_id="city1",
            country="USA",
            city="New York",
            coordinates=(40.7128, -74.0060),
        )

        assert backend.get_node_count() == 1
        assert backend.get_nodes() == ["city1"]

        attrs = backend.get_node_attributes("city1")
        assert attrs["country"] == "USA"
        assert attrs["city"] == "New York"
        assert attrs["coordinates"] == (40.7128, -74.0060)

    def test_add_and_retrieve_edges(self):
        """Test adding and retrieving edges."""
        backend = NetworkXBackend()
        backend.add_node(node_id="city1", city="New York")
        backend.add_node(node_id="city2", city="London")
        backend.add_edge(
            source_id="city1",
            target_id="city2",
            bandwidth=1000.0,
            latency=100.5,
            packet_count=100,
            protocol="TCP",
        )

        assert backend.get_edge_count() == 1
        assert backend.get_edges() == [("city1", "city2")]

        attrs = backend.get_edge_attributes("city1", "city2")
        assert attrs["bandwidth"] == 1000.0
        assert attrs["latency"] == 100.5
        assert attrs["packet_count"] == 100
        assert attrs["protocol"] == "TCP"

    def test_degree_metrics(self):
        """Test degree metrics."""
        backend = NetworkXBackend()
        backend.add_node(node_id="city1")
        backend.add_node(node_id="city2")
        backend.add_node(node_id="city3")
        backend.add_edge(source_id="city1", target_id="city2")
        backend.add_edge(source_id="city2", target_id="city3")

        assert backend.degree("city2") == 2
        assert backend.in_degree("city2") == 1
        assert backend.out_degree("city2") == 1

    def test_betweenness_centrality(self):
        """Test betweenness centrality calculation."""
        backend = NetworkXBackend()
        backend.add_node(node_id="city1")
        backend.add_node(node_id="city2")
        backend.add_node(node_id="city3")
        backend.add_edge(source_id="city1", target_id="city2")
        backend.add_edge(source_id="city2", target_id="city3")

        centrality = backend.betweenness_centrality()
        assert "city2" in centrality
        assert centrality["city2"] > 0  # Middle node should have higher centrality

    def test_closeness_centrality(self):
        """Test closeness centrality calculation."""
        backend = NetworkXBackend()
        backend.add_node(node_id="city1")
        backend.add_node(node_id="city2")
        backend.add_edge(source_id="city1", target_id="city2")

        centrality = backend.closeness_centrality()
        assert "city1" in centrality
        assert "city2" in centrality

    def test_connected_components(self):
        """Test connected components detection."""
        backend = NetworkXBackend()
        backend.add_node(node_id="city1")
        backend.add_node(node_id="city2")
        backend.add_node(node_id="city3")
        backend.add_edge(source_id="city1", target_id="city2")

        components = backend.connected_components()
        assert len(components) == 2

    def test_shortest_path(self):
        """Test shortest path finding."""
        backend = NetworkXBackend()
        backend.add_node(node_id="city1")
        backend.add_node(node_id="city2")
        backend.add_node(node_id="city3")
        backend.add_edge(source_id="city1", target_id="city2")
        backend.add_edge(source_id="city2", target_id="city3")

        path = backend.shortest_path("city1", "city3")
        assert path == ["city1", "city2", "city3"]

    def test_shortest_path_no_path(self):
        """Test shortest path when no path exists."""
        backend = NetworkXBackend()
        backend.add_node(node_id="city1")
        backend.add_node(node_id="city2")

        path = backend.shortest_path("city1", "city2")
        assert path is None

    def test_shortest_path_with_weight(self):
        """Test shortest path with weight attribute."""
        backend = NetworkXBackend()
        backend.add_node(node_id="city1")
        backend.add_node(node_id="city2")
        backend.add_node(node_id="city3")
        backend.add_edge(source_id="city1", target_id="city2", latency=100)
        backend.add_edge(source_id="city2", target_id="city3", latency=50)

        path = backend.shortest_path("city1", "city3", weight="latency")
        assert path == ["city1", "city2", "city3"]

    def test_clear(self):
        """Test clearing the graph."""
        backend = NetworkXBackend()
        backend.add_node(node_id="city1")
        backend.add_node(node_id="city2")
        backend.add_edge(source_id="city1", target_id="city2")

        backend.clear()

        assert backend.get_node_count() == 0
        assert backend.get_edge_count() == 0

    def test_copy(self):
        """Test copying the graph."""
        backend = NetworkXBackend()
        backend.add_node(node_id="city1", city="New York")
        backend.add_edge(source_id="city1", target_id="city1", bandwidth=1000.0)

        copy = backend.copy()

        assert copy.get_node_count() == backend.get_node_count()
        assert copy.get_edge_count() == backend.get_edge_count()

        # Modifying copy should not affect original
        copy.add_node(node_id="city2")
        assert backend.get_node_count() == 1
        assert copy.get_node_count() == 2

    def test_to_dict(self):
        """Test graph serialization to dict."""
        backend = NetworkXBackend()
        backend.add_node(node_id="city1", city="New York")
        backend.add_edge(source_id="city1", target_id="city1", bandwidth=1000.0)

        data = backend.to_dict()

        assert "nodes" in data
        assert "edges" in data
        assert len(data["nodes"]) == 1
        assert len(data["edges"]) == 1
        assert data["nodes"][0]["id"] == "city1"
        assert data["nodes"][0]["city"] == "New York"

    def test_from_dict(self):
        """Test graph deserialization from dict."""
        data = {
            "nodes": [
                {"id": "city1", "city": "New York"},
                {"id": "city2", "city": "London"},
            ],
            "edges": [{"source": "city1", "target": "city2", "bandwidth": 1000.0}],
        }

        backend = NetworkXBackend.from_dict(data)

        assert backend.get_node_count() == 2
        assert backend.get_edge_count() == 1
        assert backend.get_node_attributes("city1")["city"] == "New York"

    def test_directed_edges(self):
        """Test that edges are directed."""
        backend = NetworkXBackend()
        backend.add_node(node_id="city1")
        backend.add_node(node_id="city2")
        backend.add_edge(source_id="city1", target_id="city2")

        assert backend.in_degree("city1") == 0
        assert backend.out_degree("city1") == 1
        assert backend.in_degree("city2") == 1
        assert backend.out_degree("city2") == 0
