"""
Base interfaces for graph analytics algorithms.

This module defines the abstract base classes and interfaces that all
analytics algorithms must implement.

Architecture:
- Strategy Pattern: Pluggable algorithm implementations
- Interface Segregation: Small, focused interfaces
- Dependency Inversion: High-level modules depend on abstractions
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple, Type
from uuid import UUID

from ..interfaces.graph_backend import GraphBackend

# ============================================================================
# Type Definitions
# ============================================================================

GraphID = UUID
NodeID = str
Edge = Tuple[NodeID, NodeID]
EdgeWithWeight = Tuple[NodeID, NodeID, Dict[str, Any]]


# ============================================================================
# Algorithm Configuration
# ============================================================================


@dataclass
class AlgorithmConfig:
    """
    Configuration for algorithm execution.

    Attributes:
        graph_id: ID of the graph to analyze
        timeout_seconds: Maximum execution time (None for no limit)
        use_cache: Whether to use cached results
        cache_ttl_seconds: Cache time-to-live in seconds
        parameters: Algorithm-specific parameters
    """

    graph_id: GraphID
    timeout_seconds: Optional[int] = None
    use_cache: bool = True
    cache_ttl_seconds: int = 3600  # 1 hour default
    parameters: Dict[str, Any] = field(default_factory=dict)
    node_filter: Optional[Callable[[NodeID], bool]] = None
    edge_filter: Optional[Callable[[EdgeWithWeight], bool]] = None


@dataclass
class AlgorithmResult:
    """
    Result of algorithm execution.

    Attributes:
        algorithm_name: Name of the algorithm that produced this result
        graph_id: ID of the graph that was analyzed
        execution_time_ms: Execution time in milliseconds
        results: Algorithm-specific results
        metadata: Additional metadata about the computation
        cached: Whether this result was retrieved from cache
    """

    algorithm_name: str
    graph_id: GraphID
    execution_time_ms: int
    results: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    cached: bool = False


# ============================================================================
# Base Algorithm Interface
# ============================================================================


class AlgorithmStrategy(ABC):
    """
    Base interface for all analytics algorithms.

    This defines the contract that all algorithm implementations must follow.
    Algorithms should be stateless and thread-safe.
    """

    # Algorithm metadata
    name: str = "base_algorithm"
    category: str = "base"
    version: str = "1.0.0"
    description: str = "Base algorithm interface"

    # Performance characteristics
    complexity_time: str = "Unknown"  # e.g., "O(V + E)", "O(V^3)"
    complexity_space: str = "Unknown"  # e.g., "O(V)", "O(V + E)"
    recommended_max_nodes: int = 100_000

    @classmethod
    @abstractmethod
    def validate_config(cls, config: AlgorithmConfig) -> List[str]:
        """
        Validate algorithm configuration.

        Returns list of validation error messages (empty if valid).

        Args:
            config: Algorithm configuration to validate

        Returns:
            List of error messages (empty if valid)
        """
        pass

    @classmethod
    @abstractmethod
    def get_required_parameters(cls) -> List[str]:
        """
        Get list of required parameter names.

        Returns:
            List of required parameter names
        """
        pass

    @classmethod
    @abstractmethod
    def get_optional_parameters(cls) -> Dict[str, Any]:
        """
        Get default values for optional parameters.

        Returns:
            Dictionary of parameter names to default values
        """
        pass


# ============================================================================
# Centrality Algorithms
# ============================================================================


class CentralityAlgorithm(AlgorithmStrategy):
    """
    Base interface for centrality algorithms.

    Centrality algorithms measure the importance or influence of nodes
    in a graph.
    """

    category: str = "centrality"

    @abstractmethod
    def compute(self, backend: GraphBackend, config: AlgorithmConfig) -> AlgorithmResult:
        """
        Compute centrality for all nodes in the graph.

        Args:
            backend: Graph backend implementation
            config: Algorithm configuration

        Returns:
            Algorithm result with node_id -> centrality_score mapping
        """
        pass

    @abstractmethod
    def compute_for_node(
        self, backend: GraphBackend, node_id: NodeID, config: AlgorithmConfig
    ) -> float:
        """
        Compute centrality for a specific node.

        Args:
            backend: Graph backend implementation
            node_id: ID of the node to compute centrality for
            config: Algorithm configuration

        Returns:
            Centrality score for the specified node
        """
        pass

    @abstractmethod
    def get_top_nodes(
        self, backend: GraphBackend, n: int = 10, config: Optional[AlgorithmConfig] = None
    ) -> List[Tuple[NodeID, float]]:
        """
        Get top N nodes by centrality score.

        Args:
            backend: Graph backend implementation
            n: Number of top nodes to return
            config: Algorithm configuration (optional)

        Returns:
            List of (node_id, centrality_score) tuples, sorted by score descending
        """
        pass


# ============================================================================
# Community Detection Algorithms
# ============================================================================


class CommunityDetectionAlgorithm(AlgorithmStrategy):
    """
    Base interface for community detection algorithms.

    Community detection algorithms partition graph nodes into
    communities or clusters.
    """

    category: str = "community"

    @abstractmethod
    def detect_communities(self, backend: GraphBackend, config: AlgorithmConfig) -> AlgorithmResult:
        """
        Detect communities in the graph.

        Args:
            backend: Graph backend implementation
            config: Algorithm configuration

        Returns:
            Algorithm result with node_id -> community_id mapping
        """
        pass

    @abstractmethod
    def compute_modularity(
        self, backend: GraphBackend, partition: Dict[NodeID, int], config: AlgorithmConfig
    ) -> float:
        """
        Compute modularity score for a community partition.

        Modularity measures the quality of a community partition.

        Args:
            backend: Graph backend implementation
            partition: Node to community mapping
            config: Algorithm configuration

        Returns:
            Modularity score (typically between -1 and 1)
        """
        pass

    @abstractmethod
    def find_bridge_nodes(
        self, backend: GraphBackend, partition: Dict[NodeID, int], config: AlgorithmConfig
    ) -> List[NodeID]:
        """
        Find nodes that connect different communities.

        Args:
            backend: Graph backend implementation
            partition: Node to community mapping
            config: Algorithm configuration

        Returns:
            List of bridge node IDs
        """
        pass


# ============================================================================
# Path Analysis Algorithms
# ============================================================================


class PathAnalysisAlgorithm(AlgorithmStrategy):
    """
    Base interface for path analysis algorithms.

    Path analysis algorithms compute routes, distances, and
    connectivity metrics in graphs.
    """

    category: str = "path"

    @abstractmethod
    def find_shortest_path(
        self, backend: GraphBackend, source: NodeID, target: NodeID, config: AlgorithmConfig
    ) -> AlgorithmResult:
        """
        Find shortest path between two nodes.

        Args:
            backend: Graph backend implementation
            source: Source node ID
            target: Target node ID
            config: Algorithm configuration

        Returns:
            Algorithm result with path (list of node IDs) and length
        """
        pass

    @abstractmethod
    def find_k_shortest_paths(
        self, backend: GraphBackend, source: NodeID, target: NodeID, k: int, config: AlgorithmConfig
    ) -> List[List[NodeID]]:
        """
        Find k-shortest paths between two nodes.

        Args:
            backend: Graph backend implementation
            source: Source node ID
            target: Target node ID
            k: Number of paths to find
            config: Algorithm configuration

        Returns:
            List of paths (each path is a list of node IDs)
        """
        pass

    @abstractmethod
    def detect_cycles(self, backend: GraphBackend, config: AlgorithmConfig) -> AlgorithmResult:
        """
        Detect cycles in the graph.

        Args:
            backend: Graph backend implementation
            config: Algorithm configuration

        Returns:
            Algorithm result with list of cycles
        """
        pass

    @abstractmethod
    def find_strongly_connected_components(
        self, backend: GraphBackend, config: AlgorithmConfig
    ) -> AlgorithmResult:
        """
        Find strongly connected components in the graph.

        Args:
            backend: Graph backend implementation
            config: Algorithm configuration

        Returns:
            Algorithm result with list of SCCs (each SCC is a set of node IDs)
        """
        pass

    @abstractmethod
    def compute_diameter(self, backend: GraphBackend, config: AlgorithmConfig) -> int:
        """
        Compute graph diameter (longest shortest path).

        Args:
            backend: Graph backend implementation
            config: Algorithm configuration

        Returns:
            Graph diameter (number of edges in longest shortest path)
        """
        pass


# ============================================================================
# Anomaly Detection Algorithms
# ============================================================================


class AnomalyDetector(AlgorithmStrategy):
    """
    Base interface for anomaly detection algorithms.

    Anomaly detectors identify unusual patterns in graph data.
    """

    category: str = "anomaly_detection"

    @abstractmethod
    def detect(self, backend: GraphBackend, config: AlgorithmConfig) -> AlgorithmResult:
        """
        Detect anomalies in the graph.

        Args:
            backend: Graph backend implementation
            config: Algorithm configuration

        Returns:
            Algorithm result with list of detected anomalies
        """
        pass

    @abstractmethod
    def get_severity_score(self, anomaly: Dict[str, Any]) -> int:
        """
        Compute severity score for an anomaly (1-10).

        Args:
            anomaly: Anomaly data dictionary

        Returns:
            Severity score from 1 (low) to 10 (critical)
        """
        pass

    @abstractmethod
    def classify_anomaly(self, anomaly: Dict[str, Any]) -> str:
        """
        Classify anomaly by type.

        Args:
            anomaly: Anomaly data dictionary

        Returns:
            Anomaly type string
        """
        pass


# ============================================================================
# Feature Extraction
# ============================================================================


class FeatureExtractor(AlgorithmStrategy):
    """
    Base interface for feature extraction algorithms.

    Feature extractors compute features from graphs for use in
    machine learning models.
    """

    category: str = "feature_extraction"

    @abstractmethod
    def extract_features(self, backend: GraphBackend, config: AlgorithmConfig) -> AlgorithmResult:
        """
        Extract features from the graph.

        Args:
            backend: Graph backend implementation
            config: Algorithm configuration

        Returns:
            Algorithm result with feature dictionary
        """
        pass

    @abstractmethod
    def extract_node_features(
        self, backend: GraphBackend, node_id: NodeID, config: AlgorithmConfig
    ) -> Dict[str, float]:
        """
        Extract features for a specific node.

        Args:
            backend: Graph backend implementation
            node_id: ID of the node
            config: Algorithm configuration

        Returns:
            Dictionary of feature names to values
        """
        pass

    @abstractmethod
    def extract_edge_features(
        self, backend: GraphBackend, source: NodeID, target: NodeID, config: AlgorithmConfig
    ) -> Dict[str, float]:
        """
        Extract features for a specific edge.

        Args:
            backend: Graph backend implementation
            source: Source node ID
            target: Target node ID
            config: Algorithm configuration

        Returns:
            Dictionary of feature names to values
        """
        pass
