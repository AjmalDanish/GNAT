"""
Graph Backend Interface.

This module defines the abstract interface for graph operations.
All graph backend implementations must implement this interface.

Architecture:
- Clean Architecture: Interface Layer
- Dependency Inversion Principle
- Allows swapping backends (NetworkX, Neo4j, Memgraph, GraphBLAS)

Status: Phase 2 - Graph Construction Engine
"""

from abc import ABC, abstractmethod
from typing import Any


class GraphBackend(ABC):
    """Abstract interface for graph backend implementations."""

    @abstractmethod
    def add_node(
        self,
        node_id: str,
        country: str | None = None,
        city: str | None = None,
        coordinates: tuple[float, float] | None = None,
        **attributes: Any,
    ) -> None:
        """Add a node to the graph.

        Args:
            node_id: Unique identifier for the node (usually city_id)
            country: Country name
            city: City name
            coordinates: (latitude, longitude) tuple
            **attributes: Additional node attributes
        """
        pass

    @abstractmethod
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
        """Add a directed edge to the graph.

        Args:
            source_id: Source node ID
            target_id: Target node ID
            bandwidth: Bandwidth value
            latency: Latency value
            packet_count: Number of packets
            protocol: Protocol type
            **attributes: Additional edge attributes
        """
        pass

    @abstractmethod
    def get_node_count(self) -> int:
        """Return the number of nodes in the graph."""
        pass

    @abstractmethod
    def get_edge_count(self) -> int:
        """Return the number of edges in the graph."""
        pass

    @abstractmethod
    def degree(self, node_id: str) -> int:
        """Return the degree of a node."""
        pass

    @abstractmethod
    def in_degree(self, node_id: str) -> int:
        """Return the in-degree of a node."""
        pass

    @abstractmethod
    def out_degree(self, node_id: str) -> int:
        """Return the out-degree of a node."""
        pass

    @abstractmethod
    def betweenness_centrality(self) -> dict[str, float]:
        """Calculate betweenness centrality for all nodes."""
        pass

    @abstractmethod
    def closeness_centrality(self) -> dict[str, float]:
        """Calculate closeness centrality for all nodes."""
        pass

    @abstractmethod
    def connected_components(self) -> list[set[str]]:
        """Return connected components as sets of node IDs."""
        pass

    @abstractmethod
    def shortest_path(
        self, source_id: str, target_id: str, weight: str | None = None
    ) -> list[str] | None:
        """Find shortest path between two nodes.

        Args:
            source_id: Source node ID
            target_id: Target node ID
            weight: Edge attribute to use as weight (e.g., 'latency', 'bandwidth')

        Returns:
            List of node IDs forming the path, or None if no path exists
        """
        pass

    @abstractmethod
    def get_nodes(self) -> list[str]:
        """Return list of all node IDs."""
        pass

    @abstractmethod
    def get_edges(self) -> list[tuple[str, str]]:
        """Return list of all edges as (source, target) tuples."""
        pass

    @abstractmethod
    def get_node_attributes(self, node_id: str) -> dict[str, Any]:
        """Return all attributes for a node."""
        pass

    @abstractmethod
    def get_edge_attributes(
        self, source_id: str, target_id: str
    ) -> dict[str, Any] | None:
        """Return all attributes for an edge."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Remove all nodes and edges from the graph."""
        pass

    @abstractmethod
    def copy(self) -> "GraphBackend":
        """Create a copy of the graph."""
        pass

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        """Serialize graph to dictionary representation."""
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict[str, Any]) -> "GraphBackend":
        """Deserialize graph from dictionary representation."""
        pass
