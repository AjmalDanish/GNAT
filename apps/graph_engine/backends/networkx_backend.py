"""
NetworkX Backend Implementation.

This module implements the GraphBackend interface using NetworkX.

Architecture:
- Clean Architecture: Infrastructure Layer
- Implements GraphBackend interface
- Efficient graph operations using NetworkX

Status: Phase 2 - Graph Construction Engine
"""

from typing import Any

import networkx as nx

from ..interfaces.graph_backend import GraphBackend


class NetworkXBackend(GraphBackend):
    """NetworkX implementation of GraphBackend interface."""

    def __init__(self) -> None:
        """Initialize an empty directed graph."""
        self._graph: nx.DiGraph = nx.DiGraph()

    def add_node(
        self,
        node_id: str,
        country: str | None = None,
        city: str | None = None,
        coordinates: tuple[float, float] | None = None,
        **attributes: Any,
    ) -> None:
        """Add a node to the graph."""
        attrs = {}
        if country is not None:
            attrs["country"] = country
        if city is not None:
            attrs["city"] = city
        if coordinates is not None:
            attrs["coordinates"] = coordinates
        attrs.update(attributes)

        self._graph.add_node(node_id, **attrs)

    def add_edge(
        self,
        source_id: str,
        target_id: str,
        bandwidth: float | None = None,
        latency: float | None = None,
        packet_count: int | None = None,
        protocol: str | None = None,
        **attributes: Any,
    ) -> None:
        """Add a directed edge to the graph."""
        attrs = {}
        if bandwidth is not None:
            attrs["bandwidth"] = bandwidth
        if latency is not None:
            attrs["latency"] = latency
        if packet_count is not None:
            attrs["packet_count"] = packet_count
        if protocol is not None:
            attrs["protocol"] = protocol
        attrs.update(attributes)

        self._graph.add_edge(source_id, target_id, **attrs)

    def get_node_count(self) -> int:
        """Return the number of nodes in the graph."""
        return self._graph.number_of_nodes()

    def get_edge_count(self) -> int:
        """Return the number of edges in the graph."""
        return self._graph.number_of_edges()

    def degree(self, node_id: str) -> int:
        """Return the degree of a node."""
        return self._graph.degree(node_id)

    def in_degree(self, node_id: str) -> int:
        """Return the in-degree of a node."""
        return self._graph.in_degree(node_id)

    def out_degree(self, node_id: str) -> int:
        """Return the out-degree of a node."""
        return self._graph.out_degree(node_id)

    def betweenness_centrality(self) -> dict[str, float]:
        """Calculate betweenness centrality for all nodes."""
        return nx.betweenness_centrality(self._graph, k=min(100, self.get_node_count()))

    def closeness_centrality(self) -> dict[str, float]:
        """Calculate closeness centrality for all nodes."""
        # Handle disconnected graphs
        try:
            return nx.closeness_centrality(self._graph)
        except nx.NetworkXError:
            # For disconnected graphs, use harmonic centrality
            return nx.harmonic_centrality(self._graph)

    def connected_components(self) -> list[set[str]]:
        """Return weakly connected components."""
        return [set(component) for component in nx.weakly_connected_components(self._graph)]

    def shortest_path(
        self, source_id: str, target_id: str, weight: str | None = None
    ) -> list[str] | None:
        """Find shortest path between two nodes."""
        try:
            return nx.shortest_path(self._graph, source_id, target_id, weight=weight)
        except nx.NetworkXNoPath:
            return None

    def get_nodes(self) -> list[str]:
        """Return list of all node IDs."""
        return list(self._graph.nodes())

    def get_edges(self) -> list[tuple[str, str]]:
        """Return list of all edges as (source, target) tuples."""
        return list(self._graph.edges())

    def get_node_attributes(self, node_id: str) -> dict[str, Any]:
        """Return all attributes for a node."""
        return dict(self._graph.nodes[node_id])

    def get_edge_attributes(self, source_id: str, target_id: str) -> dict[str, Any] | None:
        """Return all attributes for an edge."""
        if self._graph.has_edge(source_id, target_id):
            return dict(self._graph.edges[source_id, target_id])
        return None

    def clear(self) -> None:
        """Remove all nodes and edges from the graph."""
        self._graph.clear()

    def copy(self) -> "NetworkXBackend":
        """Create a copy of the graph."""
        new_backend = NetworkXBackend()
        new_backend._graph = self._graph.copy()
        return new_backend

    def to_dict(self) -> dict[str, Any]:
        """Serialize graph to dictionary representation."""
        return {
            "nodes": [{"id": node, **self.get_node_attributes(node)} for node in self.get_nodes()],
            "edges": [
                {
                    "source": source,
                    "target": target,
                    **self.get_edge_attributes(source, target),
                }
                for source, target in self.get_edges()
            ],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "NetworkXBackend":
        """Deserialize graph from dictionary representation."""
        backend = cls()
        for node_data in data.get("nodes", []):
            node_id = node_data.pop("id")
            backend.add_node(node_id, **node_data)
        for edge_data in data.get("edges", []):
            source = edge_data.pop("source")
            target = edge_data.pop("target")
            backend.add_edge(source, target, **edge_data)
        return backend
