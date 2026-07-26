"""
Degree Centrality Algorithm.

Computes the number of connections each node has.

Complexity: O(V + E)
"""

from typing import Any, Dict, List, Optional, Tuple

from ...interfaces import CentralityAlgorithm, AlgorithmConfig, AlgorithmResult
from ...exceptions import AlgorithmExecutionError


class DegreeCentralityAlgorithm(CentralityAlgorithm):
    """Degree centrality computation.
    
    Measures node importance based on the number of connections.
    Simple but effective for identifying highly connected nodes (hubs).
    """

    name = "degree_centrality"
    category = "centrality"
    version = "1.0.0"
    description = "Computes degree centrality for all nodes in the graph"
    complexity_time = "O(V + E)"
    complexity_space = "O(V)"
    recommended_max_nodes = 1_000_000

    @classmethod
    def validate_config(cls, config: AlgorithmConfig) -> List[str]:
        """Validate configuration parameters."""
        errors = []

        if config.node_filter and not callable(config.node_filter):
            errors.append("node_filter must be callable")
        if config.edge_filter and not callable(config.edge_filter):
            errors.append("edge_filter must be callable")

        return errors

    @classmethod
    def get_required_parameters(cls) -> List[str]:
        """Degree centrality has no required parameters."""
        return []

    @classmethod
    def get_optional_parameters(cls) -> Dict[str, Any]:
        """Default values for optional parameters."""
        return {
            "weighted": False,
            "normalize": True,
        }

    def compute(
        self,
        backend,
        config: AlgorithmConfig,
    ) -> AlgorithmResult:
        """
        Compute degree centrality for all nodes.
        
        Args:
            backend: Graph backend implementation
            config: Algorithm configuration
            
        Returns:
            Algorithm result with node_id -> centrality_score mapping
        """
        import time

        start_time = time.time()

        # Get graph info
        node_ids = backend.get_nodes()
        edge_filter = config.edge_filter or (lambda x: True)

        # Compute degrees
        degrees = {}
        weighted = config.parameters.get("weighted", False)
        normalize = config.parameters.get("normalize", True)
        node_filter = config.node_filter or (lambda x: x in node_ids)

        for node_id in node_ids:
            if not node_filter(node_id):
                continue

            neighbors = backend.get_neighbors(node_id)
            filtered_neighbors = [n for n in neighbors if edge_filter((node_id, n, {}))]

            if weighted:
                # Sum edge weights
                degree = 0.0
                for neighbor_id in filtered_neighbors:
                    edges = backend.get_edges(node_id, neighbor_id)
                    for edge in edges:
                        weight = edge.get("weight", 1.0)
                        degree += weight
            else:
                # Count edges
                degree = len(filtered_neighbors)

            degrees[node_id] = degree

        # Normalize if requested
        if normalize and degrees:
            max_degree = max(degrees.values()) if degrees else 1
            degrees = {node: val / max_degree for node, val in degrees.items()}

        execution_time_ms = int((time.time() - start_time) * 1000)

        return AlgorithmResult(
            algorithm_name=self.name,
            graph_id=config.graph_id,
            execution_time_ms=execution_time_ms,
            results=degrees,
            metadata={
                "weighted": weighted,
                "normalize": normalize,
                "node_count": len(degrees),
                "max_degree": max(degrees.values()) if degrees else 0,
            },
        )

    def compute_for_node(
        self,
        backend,
        node_id: str,
        config: AlgorithmConfig,
    ) -> float:
        """
        Compute degree centrality for a specific node.
        
        Args:
            backend: Graph backend implementation
            node_id: ID of the node to compute centrality for
            config: Algorithm configuration
            
        Returns:
            Centrality score for the specified node
        """
        weighted = config.parameters.get("weighted", False)
        normalize = config.parameters.get("normalize", True)
        edge_filter = config.edge_filter or (lambda x: True)

        neighbors = backend.get_neighbors(node_id)
        filtered_neighbors = [n for n in neighbors if edge_filter((node_id, n, {}))]

        if weighted:
            degree = 0.0
            for neighbor_id in filtered_neighbors:
                edges = backend.get_edges(node_id, neighbor_id)
                for edge in edges:
                    degree += edge.get("weight", 1.0)
        else:
            degree = len(filtered_neighbors)

        # Normalize by max degree if requested
        if normalize:
            # Need to compute max degree for normalization
            all_nodes = backend.get_nodes()
            max_degree = 0
            for n in all_nodes:
                neighbors = backend.get_neighbors(n)
                max_degree = max(max_degree, len(neighbors))
            if max_degree > 0:
                degree = degree / max_degree

        return degree

    def get_top_nodes(
        self,
        backend,
        n: int = 10,
        config: Optional[AlgorithmConfig] = None,
    ) -> List[Tuple[str, float]]:
        """
        Get top N nodes by centrality score.
        
        Args:
            backend: Graph backend implementation
            n: Number of top nodes to return
            config: Algorithm configuration (optional)
            
        Returns:
            List of (node_id, centrality_score) tuples, sorted descending
        """
        if config is None:
            from uuid import uuid4
            config = AlgorithmConfig(graph_id=uuid4())

        result = self.compute(backend, config)

        # Sort by centrality score descending
        sorted_items = sorted(result.results.items(), key=lambda x: x[1], reverse=True)

        return sorted_items[:n]