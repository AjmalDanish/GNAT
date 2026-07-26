"""
Graph Metrics Service.

This module calculates various metrics on graphs using the configured backend.

Architecture:
- Clean Architecture: Application Layer
- Business logic for graph analysis
- Works through GraphBackend interface

Status: Phase 2 - Graph Construction Engine
"""

from typing import Any

from ..interfaces.graph_backend import GraphBackend


class GraphMetrics:
    """Service for calculating graph metrics."""

    def __init__(self, backend: GraphBackend) -> None:
        """Initialize GraphMetrics.

        Args:
            backend: GraphBackend instance to analyze
        """
        self.backend = backend

    def calculate_degree_metrics(self) -> dict[str, dict[str, int]]:
        """Calculate degree metrics for all nodes.

        Returns:
            Dict mapping node_id to {degree, in_degree, out_degree}
        """
        metrics = {}
        for node_id in self.backend.get_nodes():
            metrics[node_id] = {
                "degree": self.backend.degree(node_id),
                "in_degree": self.backend.in_degree(node_id),
                "out_degree": self.backend.out_degree(node_id),
            }
        return metrics

    def calculate_centrality_metrics(self) -> dict[str, dict[str, float]]:
        """Calculate centrality metrics for all nodes.

        Returns:
            Dict mapping node_id to {betweenness, closeness}
        """
        betweenness = self.backend.betweenness_centrality()
        closeness = self.backend.closeness_centrality()

        metrics = {}
        # Get all unique node IDs from both metrics
        all_nodes = set(betweenness.keys()) | set(closeness.keys())

        for node_id in all_nodes:
            metrics[node_id] = {
                "betweenness": betweenness.get(node_id, 0.0),
                "closeness": closeness.get(node_id, 0.0),
            }
        return metrics

    def calculate_connectivity_metrics(self) -> dict[str, Any]:
        """Calculate connectivity metrics for the graph.

        Returns:
            Dict with connectivity metrics:
                - connected_components: Number of connected components
                - largest_component_size: Size of largest component
                - node_count: Total number of nodes
                - edge_count: Total number of edges
                - density: Graph density
        """
        components = self.backend.connected_components()
        node_count = self.backend.get_node_count()
        edge_count = self.backend.get_edge_count()

        max_component_size = max((len(c) for c in components), default=0)

        # Calculate density (edges / possible_edges)
        if node_count > 1:
            possible_edges = node_count * (node_count - 1)
            density = edge_count / possible_edges if possible_edges > 0 else 0.0
        else:
            density = 0.0

        return {
            "connected_components": len(components),
            "largest_component_size": max_component_size,
            "node_count": node_count,
            "edge_count": edge_count,
            "density": density,
        }

    def find_shortest_paths(
        self,
        source_id: str | None = None,
        target_id: str | None = None,
        weight: str | None = None,
    ) -> dict[str, list[str] | None]:
        """Find shortest paths between nodes.

        Args:
            source_id: Source node ID (or None for all nodes)
            target_id: Target node ID (or None for all nodes)
            weight: Edge attribute to use as weight

        Returns:
            Dict mapping (source, target) tuples to path lists
        """
        paths = {}

        if source_id and target_id:
            # Single path
            path = self.backend.shortest_path(source_id, target_id, weight)
            paths[(source_id, target_id)] = path
        elif source_id:
            # Paths from source to all nodes
            for target in self.backend.get_nodes():
                if target != source_id:
                    path = self.backend.shortest_path(source_id, target, weight)
                    paths[(source_id, target)] = path
        else:
            # All pairs shortest paths
            for src in self.backend.get_nodes():
                for tgt in self.backend.get_nodes():
                    if src != tgt:
                        path = self.backend.shortest_path(src, tgt, weight)
                        paths[(src, tgt)] = path

        return paths

    def get_node_summary(self, node_id: str) -> dict[str, Any]:
        """Get a summary of a node and its connections.

        Args:
            node_id: Node ID to summarize

        Returns:
            Dict with node attributes and metrics
        """
        attrs = self.backend.get_node_attributes(node_id)

        return {
            "id": node_id,
            "attributes": attrs,
            "degree": self.backend.degree(node_id),
            "in_degree": self.backend.in_degree(node_id),
            "out_degree": self.backend.out_degree(node_id),
        }

    def get_edge_summary(self, source_id: str, target_id: str) -> dict[str, Any]:
        """Get a summary of an edge.

        Args:
            source_id: Source node ID
            target_id: Target node ID

        Returns:
            Dict with edge attributes and metadata
        """
        attrs = self.backend.get_edge_attributes(source_id, target_id)

        if attrs is None:
            return {}

        return {
            "source": source_id,
            "target": target_id,
            "attributes": attrs,
        }

    def get_graph_summary(self) -> dict[str, Any]:
        """Get a comprehensive summary of the graph.

        Returns:
            Dict with all graph metrics
        """
        return {
            "nodes": self.backend.get_node_count(),
            "edges": self.backend.get_edge_count(),
            "connectivity": self.calculate_connectivity_metrics(),
            "degree_metrics": self.calculate_degree_metrics(),
            "centrality_metrics": self.calculate_centrality_metrics(),
        }
