"""
Repository layer for graph analytics data.

This module provides data access abstraction for analytics results,
anomalies, and historical metrics.

Architecture:
- Repository Pattern: Abstraction over database operations
- Clean Architecture: Separation of data access from business logic
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from .interfaces import AlgorithmResult

# ============================================================================
# Repository Interfaces
# ============================================================================


class AnalyticsRepository(ABC):
    """
    Abstract base class for analytics repositories.

    This defines the interface that all analytics repositories
    must implement for data access operations.
    """

    @abstractmethod
    def save_result(self, result: AlgorithmResult) -> str:
        """
        Save analytics result to persistent storage.

        Args:
            result: Algorithm result to save

        Returns:
            ID of saved record
        """
        pass

    @abstractmethod
    def get_result(self, result_id: str) -> Optional[AlgorithmResult]:
        """
        Retrieve analytics result by ID.

        Args:
            result_id: ID of result to retrieve

        Returns:
            Algorithm result or None if not found
        """
        pass

    @abstractmethod
    def get_latest_result(
        self, graph_id: UUID, algorithm_name: str
    ) -> Optional[AlgorithmResult]:
        """
        Get latest result for a graph and algorithm.

        Args:
            graph_id: Graph ID
            algorithm_name: Algorithm name

        Returns:
            Latest result or None if not found
        """
        pass

    @abstractmethod
    def get_results_by_date_range(
        self, graph_id: UUID, start_date: datetime, end_date: datetime
    ) -> List[AlgorithmResult]:
        """
        Get results within date range.

        Args:
            graph_id: Graph ID
            start_date: Start of date range
            end_date: End of date range

        Returns:
            List of results
        """
        pass

    @abstractmethod
    def delete_old_results(self, before_date: datetime) -> int:
        """
        Delete results older than specified date.

        Args:
            before_date: Cutoff date

        Returns:
            Number of records deleted
        """
        pass


# ============================================================================
# In-Memory Repository Implementation
# ============================================================================


@dataclass
class StoredResult:
    """
    Stored result with metadata.

    Attributes:
        id: Unique identifier
        result: Algorithm result
        created_at: Timestamp when result was stored
    """

    id: str
    result: AlgorithmResult
    created_at: datetime = field(default_factory=datetime.utcnow)


class InMemoryAnalyticsRepository(AnalyticsRepository):
    """
    In-memory implementation of analytics repository.

    This implementation stores results in memory and is suitable
    for testing and development. Production should use a database-backed
    implementation.
    """

    def __init__(self) -> None:
        """Initialize in-memory repository."""
        self._results: Dict[str, StoredResult] = {}
        self._by_graph: Dict[UUID, Dict[str, List[str]]] = {}
        self._by_algorithm: Dict[str, List[str]] = {}

    def save_result(self, result: AlgorithmResult) -> str:
        """
        Save analytics result to persistent storage.

        Args:
            result: Algorithm result to save

        Returns:
            ID of saved record
        """
        result_id = str(uuid4())
        stored = StoredResult(id=result_id, result=result)

        # Store result
        self._results[result_id] = stored

        # Index by graph
        graph_id = result.graph_id
        if graph_id not in self._by_graph:
            self._by_graph[graph_id] = {}
        algorithm_name = result.algorithm_name
        if algorithm_name not in self._by_graph[graph_id]:
            self._by_graph[graph_id][algorithm_name] = []
        self._by_graph[graph_id][algorithm_name].append(result_id)

        # Index by algorithm
        if algorithm_name not in self._by_algorithm:
            self._by_algorithm[algorithm_name] = []
        self._by_algorithm[algorithm_name].append(result_id)

        return result_id

    def get_result(self, result_id: str) -> Optional[AlgorithmResult]:
        """
        Retrieve analytics result by ID.

        Args:
            result_id: ID of result to retrieve

        Returns:
            Algorithm result or None if not found
        """
        stored = self._results.get(result_id)
        return stored.result if stored else None

    def get_latest_result(
        self, graph_id: UUID, algorithm_name: str
    ) -> Optional[AlgorithmResult]:
        """
        Get latest result for a graph and algorithm.

        Args:
            graph_id: Graph ID
            algorithm_name: Algorithm name

        Returns:
            Latest result or None if not found
        """
        if graph_id not in self._by_graph:
            return None
        if algorithm_name not in self._by_graph[graph_id]:
            return None

        # Get most recent result
        result_ids = self._by_graph[graph_id][algorithm_name]
        if not result_ids:
            return None

        # Sort by creation time and get latest
        results_with_time = [(self._results[rid].created_at, rid) for rid in result_ids]
        results_with_time.sort(reverse=True)

        latest_id = results_with_time[0][1]
        return self._results[latest_id].result

    def get_results_by_date_range(
        self, graph_id: UUID, start_date: datetime, end_date: datetime
    ) -> List[AlgorithmResult]:
        """
        Get results within date range.

        Args:
            graph_id: Graph ID
            start_date: Start of date range
            end_date: End of date range

        Returns:
            List of results
        """
        results = []

        if graph_id not in self._by_graph:
            return results

        for algorithm_name, result_ids in self._by_graph[graph_id].items():
            for result_id in result_ids:
                stored = self._results[result_id]
                if start_date <= stored.created_at <= end_date:
                    results.append(stored.result)

        # Sort by creation time
        results.sort(key=lambda r: r.metadata.get("created_at", datetime.min))
        return results

    def delete_old_results(self, before_date: datetime) -> int:
        """
        Delete results older than specified date.

        Args:
            before_date: Cutoff date

        Returns:
            Number of records deleted
        """
        to_delete = [
            rid
            for rid, stored in self._results.items()
            if stored.created_at < before_date
        ]

        for rid in to_delete:
            self._delete_result(rid)

        return len(to_delete)

    def _delete_result(self, result_id: str) -> None:
        """
        Delete result by ID.

        Args:
            result_id: ID of result to delete
        """
        if result_id not in self._results:
            return

        stored = self._results[result_id]
        graph_id = stored.result.graph_id
        algorithm_name = stored.result.algorithm_name

        # Remove from main storage
        del self._results[result_id]

        # Remove from graph index
        if graph_id in self._by_graph:
            if algorithm_name in self._by_graph[graph_id]:
                self._by_graph[graph_id][algorithm_name].remove(result_id)
                if not self._by_graph[graph_id][algorithm_name]:
                    del self._by_graph[graph_id][algorithm_name]
            if not self._by_graph[graph_id]:
                del self._by_graph[graph_id]

        # Remove from algorithm index
        if algorithm_name in self._by_algorithm:
            self._by_algorithm[algorithm_name].remove(result_id)
            if not self._by_algorithm[algorithm_name]:
                del self._by_algorithm[algorithm_name]

    def clear(self) -> None:
        """Clear all stored results."""
        self._results.clear()
        self._by_graph.clear()
        self._by_algorithm.clear()

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get repository statistics.

        Returns:
            Dictionary with statistics
        """
        return {
            "total_results": len(self._results),
            "graphs_stored": len(self._by_graph),
            "algorithms_stored": len(self._by_algorithm),
        }


# ============================================================================
# Factory Functions
# ============================================================================


def create_repository(repository_type: str = "memory") -> AnalyticsRepository:
    """
    Create a repository instance.

    Args:
        repository_type: Type of repository ("memory" or "database")

    Returns:
        Repository instance

    Raises:
        ValueError: If repository type is not supported
    """
    if repository_type == "memory":
        return InMemoryAnalyticsRepository()
    elif repository_type == "database":
        raise NotImplementedError("Database repository not yet implemented")
    else:
        raise ValueError(
            f"Unsupported repository type: {repository_type}. "
            f"Supported types: memory, database"
        )


# Singleton repository instance (can be overridden with dependency injection)
_default_repository: Optional[AnalyticsRepository] = None


def get_default_repository() -> AnalyticsRepository:
    """
    Get the default repository instance.

    Returns:
        Default repository instance (creates if not exists)
    """
    global _default_repository
    if _default_repository is None:
        _default_repository = create_repository("memory")
    return _default_repository


def set_default_repository(repository: AnalyticsRepository) -> None:
    """
    Set the default repository instance.

    Args:
        repository: Repository instance to use as default
    """
    global _default_repository
    _default_repository = repository


__all__ = [
    # Interfaces
    "AnalyticsRepository",
    # Implementations
    "InMemoryAnalyticsRepository",
    # Factory functions
    "create_repository",
    "get_default_repository",
    "set_default_repository",
    # Data classes
    "StoredResult",
]
