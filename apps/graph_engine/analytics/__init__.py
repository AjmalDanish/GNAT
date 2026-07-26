"""
Graph Analytics Module

This module provides comprehensive graph analytics capabilities including:
- Centrality analysis (degree, betweenness, closeness, PageRank)
- Community detection (Louvain, Girvan-Newman)
- Path analysis (shortest paths, cycles, connectivity)
- Anomaly detection (rule-based, statistical, graph-based)
- Feature extraction (for ML models)

Architecture:
- Clean Architecture: Domain, Application, Infrastructure layers
- Strategy Pattern: Pluggable algorithm implementations
- Registry Pattern: Dynamic algorithm discovery and registration
- Repository Pattern: Data access abstraction

Status: Phase 3 - Graph Analytics & Anomaly Detection Foundation
"""

__version__ = "1.0.0"

from .exceptions import (
    AlgorithmExecutionError,
    AlgorithmNotFoundError,
    AlgorithmTimeoutError,
    GraphAnalyticsError,
    InvalidGraphError,
)

# Export main interfaces and services
from .interfaces import (
    AlgorithmStrategy,
    AnomalyDetector,
    CentralityAlgorithm,
    CommunityDetectionAlgorithm,
    FeatureExtractor,
    PathAnalysisAlgorithm,
)
from .registry import AlgorithmRegistry

__all__ = [
    # Interfaces
    "AlgorithmStrategy",
    "CentralityAlgorithm",
    "CommunityDetectionAlgorithm",
    "PathAnalysisAlgorithm",
    "AnomalyDetector",
    "FeatureExtractor",
    # Exceptions
    "GraphAnalyticsError",
    "AlgorithmExecutionError",
    "AlgorithmNotFoundError",
    "InvalidGraphError",
    "AlgorithmTimeoutError",
    # Registry
    "AlgorithmRegistry",
]
