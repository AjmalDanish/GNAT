"""
Algorithm Registry for graph analytics algorithms.

This module implements a registry pattern for managing analytics algorithms.
Algorithms can be registered, retrieved, and queried dynamically.

Architecture:
- Registry Pattern: Centralized algorithm discovery
- Singleton: Single registry instance per process
- Thread-safe: Safe for concurrent access
"""

from __future__ import annotations

import threading
from typing import Any, Callable, Dict, List, Optional, Type

from .interfaces import (
    AlgorithmStrategy,
)


class AlgorithmRegistry:
    """
    Registry for managing analytics algorithms.

    This class provides a centralized registry for all analytics algorithms.
    Algorithms can be registered by category and retrieved for execution.

    Thread-safe singleton implementation.
    """

    _instance: Optional[AlgorithmRegistry] = None
    _lock: threading.Lock = threading.Lock()

    def __new__(cls) -> AlgorithmRegistry:
        """
        Get singleton instance.

        Returns:
            AlgorithmRegistry singleton instance
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize()
        return cls._instance

    def _initialize(self) -> None:
        """Initialize registry data structures."""
        self._algorithms: Dict[str, Type[AlgorithmStrategy]] = {}
        self._by_category: Dict[str, Dict[str, Type[AlgorithmStrategy]]] = {}
        self._metadata: Dict[str, Dict[str, Any]] = {}

    def register(
        self, algorithm_class: Type[AlgorithmStrategy], name: Optional[str] = None
    ) -> None:
        """
        Register an algorithm class.

        Args:
            algorithm_class: Algorithm class to register
            name: Optional custom name (defaults to class name)

        Raises:
            ValueError: If algorithm class doesn't have required metadata
            ValueError: If algorithm with same name already registered
        """
        # Validate algorithm class
        if not hasattr(algorithm_class, "name"):
            raise ValueError(
                f"Algorithm class {algorithm_class.__name__} must have a 'name' attribute"
            )
        if not hasattr(algorithm_class, "category"):
            raise ValueError(
                f"Algorithm class {algorithm_class.__name__} must have a 'category' attribute"
            )

        algorithm_name = name or algorithm_class.name

        # Check for duplicates
        if algorithm_name in self._algorithms:
            raise ValueError(f"Algorithm '{algorithm_name}' is already registered")

        # Register algorithm
        self._algorithms[algorithm_name] = algorithm_class

        # Register by category
        category = algorithm_class.category
        if category not in self._by_category:
            self._by_category[category] = {}
        self._by_category[category][algorithm_name] = algorithm_class

        # Store metadata
        self._metadata[algorithm_name] = {
            "class_name": algorithm_class.__name__,
            "module": algorithm_class.__module__,
            "category": category,
            "version": getattr(algorithm_class, "version", "1.0.0"),
            "description": getattr(algorithm_class, "description", ""),
            "complexity_time": getattr(algorithm_class, "complexity_time", "Unknown"),
            "complexity_space": getattr(algorithm_class, "complexity_space", "Unknown"),
            "recommended_max_nodes": getattr(algorithm_class, "recommended_max_nodes", 100_000),
        }

    def register_decorator(
        self, name: Optional[str] = None
    ) -> Callable[[Type[AlgorithmStrategy]], Type[AlgorithmStrategy]]:
        """
        Decorator for registering algorithms.

        Usage:
            @registry.register_decorator("my_algorithm")
            class MyAlgorithm(CentralityAlgorithm):
                name = "my_algorithm"
                category = "centrality"
                # ...

        Args:
            name: Optional custom name

        Returns:
            Decorator function
        """

        def decorator(algorithm_class: Type[AlgorithmStrategy]) -> Type[AlgorithmStrategy]:
            self.register(algorithm_class, name)
            return algorithm_class

        return decorator

    def get(self, algorithm_name: str) -> Type[AlgorithmStrategy]:
        """
        Get algorithm class by name.

        Args:
            algorithm_name: Name of algorithm to retrieve

        Returns:
            Algorithm class

        Raises:
            KeyError: If algorithm not found
        """
        if algorithm_name not in self._algorithms:
            available = ", ".join(self.list_algorithms())
            raise KeyError(
                f"Algorithm '{algorithm_name}' not found. " f"Available algorithms: {available}"
            )
        return self._algorithms[algorithm_name]

    def get_by_category(self, category: str) -> Dict[str, Type[AlgorithmStrategy]]:
        """
        Get all algorithms in a category.

        Args:
            category: Algorithm category

        Returns:
            Dictionary of algorithm names to classes
        """
        return self._by_category.get(category, {}).copy()

    def get_metadata(self, algorithm_name: str) -> Dict[str, Any]:
        """
        Get algorithm metadata.

        Args:
            algorithm_name: Name of algorithm

        Returns:
            Dictionary of metadata

        Raises:
            KeyError: If algorithm not found
        """
        if algorithm_name not in self._metadata:
            raise KeyError(f"Algorithm '{algorithm_name}' not found")
        return self._metadata[algorithm_name].copy()

    def list_algorithms(self, category: Optional[str] = None) -> List[str]:
        """
        List registered algorithm names.

        Args:
            category: Optional category filter

        Returns:
            List of algorithm names
        """
        if category is None:
            return sorted(self._algorithms.keys())
        return sorted(self._by_category.get(category, {}).keys())

    def list_categories(self) -> List[str]:
        """
        List registered algorithm categories.

        Returns:
            List of category names
        """
        return sorted(self._by_category.keys())

    def is_registered(self, algorithm_name: str) -> bool:
        """
        Check if algorithm is registered.

        Args:
            algorithm_name: Name of algorithm

        Returns:
            True if registered, False otherwise
        """
        return algorithm_name in self._algorithms

    def unregister(self, algorithm_name: str) -> None:
        """
        Unregister an algorithm.

        Args:
            algorithm_name: Name of algorithm to unregister

        Raises:
            KeyError: If algorithm not found
        """
        if algorithm_name not in self._algorithms:
            raise KeyError(f"Algorithm '{algorithm_name}' not found")

        # Get category before removal
        algorithm = self._algorithms[algorithm_name]
        category = algorithm.category

        # Remove from main registry
        del self._algorithms[algorithm_name]

        # Remove from category registry
        if category in self._by_category and algorithm_name in self._by_category[category]:
            del self._by_category[category][algorithm_name]
            if not self._by_category[category]:
                del self._by_category[category]

        # Remove metadata
        del self._metadata[algorithm_name]

    def clear(self) -> None:
        """Clear all registered algorithms."""
        self._algorithms.clear()
        self._by_category.clear()
        self._metadata.clear()

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get registry statistics.

        Returns:
            Dictionary with statistics
        """
        return {
            "total_algorithms": len(self._algorithms),
            "total_categories": len(self._by_category),
            "algorithms_by_category": {
                category: len(algorithms) for category, algorithms in self._by_category.items()
            },
        }


# Global registry instance
registry = AlgorithmRegistry()


def get_registry() -> AlgorithmRegistry:
    """
    Get the global algorithm registry instance.

    Returns:
        AlgorithmRegistry singleton instance
    """
    return registry


# Register base interfaces for reference
__all__ = [
    "AlgorithmRegistry",
    "get_registry",
    "registry",
]
