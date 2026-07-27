"""
Service orchestration for graph analytics.

This module provides high-level services that coordinate algorithm execution,
caching, and result persistence.

Architecture:
- Service Layer: Orchestrates algorithm execution
- Caching: Redis caching for expensive computations
- Dependency Injection: Backend and cache injected
"""

from __future__ import annotations

import sys
import time
from dataclasses import dataclass, replace
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Type
from uuid import UUID
import signal

from ...interfaces.graph_backend import GraphBackend
from ..exceptions import (
    AlgorithmExecutionError,
    AlgorithmTimeoutError,
    InvalidConfigError,
)
from ..interfaces import (
    AlgorithmConfig,
    AlgorithmResult,
    AlgorithmStrategy,
)
from ..registry import AlgorithmRegistry, get_registry


@dataclass
class CacheConfig:
    """
    Configuration for caching.

    Attributes:
        enabled: Whether caching is enabled
        ttl_seconds: Default time-to-live in seconds
        key_prefix: Prefix for cache keys
        max_size_bytes: Maximum cache size (optional, for monitoring)
    """

    enabled: bool = True
    ttl_seconds: int = 3600  # 1 hour
    key_prefix: str = "graph_analytics:"
    max_size_bytes: Optional[int] = None


class CacheAdapter:
    """
    Adapter for cache operations.

    This provides an abstraction layer for cache operations.
    Concrete implementations will use Redis, Memcached, or in-memory cache.
    """

    def __init__(self, config: CacheConfig) -> None:
        """
        Initialize cache adapter.

        Args:
            config: Cache configuration
        """
        self.config = config
        self._cache: Dict[str, tuple[Any, datetime]] = {}
        self._enabled = config.enabled

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found or expired
        """
        if not self._enabled:
            return None

        cache_key = self._make_key(key)

        if cache_key not in self._cache:
            return None

        value, expiry = self._cache[cache_key]

        # Check if expired
        if datetime.utcnow() > expiry:
            del self._cache[cache_key]
            return None

        return value

    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Time-to-live in seconds (uses config default if None)
        """
        if not self._enabled:
            return

        cache_key = self._make_key(key)
        ttl = ttl_seconds or self.config.ttl_seconds
        expiry = datetime.utcnow() + timedelta(seconds=ttl)

        self._cache[cache_key] = (value, expiry)

    def delete(self, key: str) -> None:
        """
        Delete value from cache.

        Args:
            key: Cache key
        """
        if not self._enabled:
            return

        cache_key = self._make_key(key)
        self._cache.pop(cache_key, None)

    def delete_pattern(self, pattern: str) -> None:
        """
        Delete all keys matching pattern.

        Args:
            pattern: Pattern to match (supports * wildcard)
        """
        if not self._enabled:
            return

        # Simple pattern matching for in-memory cache
        prefix = pattern.rstrip("*")
        keys_to_delete = [
            key for key in self._cache.keys() if key.startswith(self.config.key_prefix + prefix)
        ]

        for key in keys_to_delete:
            del self._cache[key]

    def clear(self) -> None:
        """Clear all cached values."""
        self._cache.clear()

    def _make_key(self, key: str) -> str:
        """
        Create full cache key with prefix.

        Args:
            key: Original key

        Returns:
            Full cache key with prefix
        """
        return f"{self.config.key_prefix}{key}"

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        return {
            "enabled": self._enabled,
            "keys": len(self._cache),
            "key_prefix": self.config.key_prefix,
        }


class AlgorithmExecutor:
    """
    Executes analytics algorithms with caching and error handling.

    This class provides a consistent interface for executing algorithms
    with support for caching, timeouts, and error handling.
    """

    def __init__(
        self,
        backend: GraphBackend,
        cache_adapter: Optional[CacheAdapter] = None,
        registry: Optional[AlgorithmRegistry] = None,
    ) -> None:
        """
        Initialize algorithm executor.

        Args:
            backend: Graph backend implementation
            cache_adapter: Optional cache adapter
            registry: Optional algorithm registry (uses global if None)
        """
        self.backend = backend
        self.cache = cache_adapter or CacheAdapter(CacheConfig(enabled=False))
        self.registry = registry or get_registry()
        # Track cache keys by graph_id for invalidation
        self._graph_cache_keys: Dict[UUID, set[str]] = {}

    def execute(
        self, algorithm_name: str, config: AlgorithmConfig, timeout_seconds: Optional[int] = None
    ) -> AlgorithmResult:
        """
        Execute an algorithm.

        Args:
            algorithm_name: Name of algorithm to execute
            config: Algorithm configuration
            timeout_seconds: Optional timeout override

        Returns:
            Algorithm execution result

        Raises:
            AlgorithmNotFoundError: If algorithm not found
            InvalidConfigError: If configuration is invalid
            AlgorithmExecutionError: If execution fails
            AlgorithmTimeoutError: If execution times out
        """
        # Get algorithm class
        algorithm_class = self._get_algorithm(algorithm_name)

        # Validate configuration
        errors = algorithm_class.validate_config(config)
        if errors:
            raise InvalidConfigError(
                f"Invalid configuration for algorithm '{algorithm_name}'", config_errors=errors
            )

        # Check cache
        if config.use_cache:
            cached_result = self._get_from_cache(algorithm_name, config)
            if cached_result is not None:
                # Return a copy with cached=True to avoid mutating cached results
                return replace(cached_result, cached=True)

        # Execute algorithm
        result = self._execute_with_timeout(
            algorithm_class, config, timeout_seconds or config.timeout_seconds
        )

        # Store in cache
        if config.use_cache:
            self._store_in_cache(algorithm_name, config, result, config.cache_ttl_seconds)

        return result

    def _get_algorithm(self, algorithm_name: str) -> Type[AlgorithmStrategy]:
        """
        Get algorithm class by name.

        Args:
            algorithm_name: Name of algorithm

        Returns:
            Algorithm class

        Raises:
            AlgorithmNotFoundError: If algorithm not found
        """
        try:
            return self.registry.get(algorithm_name)
        except KeyError as e:
            from ..exceptions import AlgorithmNotFoundError

            raise AlgorithmNotFoundError(
                algorithm_name=algorithm_name,
                details={"available": self.registry.list_algorithms()},
            ) from e

    def _execute_with_timeout(
        self,
        algorithm_class: Type[AlgorithmStrategy],
        config: AlgorithmConfig,
        timeout_seconds: Optional[int],
    ) -> AlgorithmResult:
        """
        Execute algorithm with timeout.

        Args:
            algorithm_class: Algorithm class to instantiate and execute
            config: Algorithm configuration
            timeout_seconds: Timeout in seconds

        Returns:
            Algorithm result

        Raises:
            AlgorithmTimeoutError: If execution times out
            AlgorithmExecutionError: If execution fails
        """
        # Create algorithm instance
        algorithm = algorithm_class()

        # Execute with timeout if specified
        if timeout_seconds is not None:
            # Unix-only: Use signal-based timeout for better precision
            # Windows does not support SIGALRM (Application Control policy limitation)
            if sys.platform != 'win32':

                def timeout_handler(signum: int, frame: Any) -> None:
                    raise AlgorithmTimeoutError(
                        f"Algorithm '{algorithm.name}' exceeded timeout of {timeout_seconds} seconds",
                        algorithm_name=algorithm.name,
                        timeout_seconds=timeout_seconds,
                    )

                # Set signal handler
                original_handler = signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(timeout_seconds)

                try:
                    result = self._execute_algorithm(algorithm, config)
                finally:
                    # Reset signal handler
                    signal.alarm(0)
                    signal.signal(signal.SIGALRM, original_handler)
            else:
                # Windows: Timeout not supported, execute without timeout
                # Signal.SIGALRM is not available on Windows platform
                result = self._execute_algorithm(algorithm, config)
        else:
            result = self._execute_algorithm(algorithm, config)

        return result

    def _execute_algorithm(
        self, algorithm: AlgorithmStrategy, config: AlgorithmConfig
    ) -> AlgorithmResult:
        """
        Execute algorithm instance.

        Args:
            algorithm: Algorithm instance
            config: Algorithm configuration

        Returns:
            Algorithm result

        Raises:
            AlgorithmExecutionError: If execution fails
        """
        start_time = time.time()

        try:
            # Call appropriate method based on algorithm type
            if hasattr(algorithm, "compute"):
                # Centrality algorithm
                result = algorithm.compute(self.backend, config)
            elif hasattr(algorithm, "detect_communities"):
                # Community detection algorithm
                result = algorithm.detect_communities(self.backend, config)
            elif hasattr(algorithm, "find_shortest_path"):
                # Path analysis algorithm
                result = algorithm.find_shortest_path(
                    self.backend,
                    config.parameters.get("source", ""),
                    config.parameters.get("target", ""),
                    config,
                )
            elif hasattr(algorithm, "detect"):
                # Anomaly detector
                result = algorithm.detect(self.backend, config)
            elif hasattr(algorithm, "extract_features"):
                # Feature extractor
                result = algorithm.extract_features(self.backend, config)
            else:
                raise AlgorithmExecutionError(
                    f"Algorithm '{algorithm.name}' has no known execution method",
                    algorithm_name=algorithm.name,
                )

            # Add execution time
            execution_time_ms = int((time.time() - start_time) * 1000)

            # Add metadata if not present
            if not hasattr(result, "execution_time_ms"):
                result.execution_time_ms = execution_time_ms
            if not hasattr(result, "algorithm_name"):
                result.algorithm_name = algorithm.name
            if not hasattr(result, "graph_id"):
                result.graph_id = config.graph_id
            if not hasattr(result, "metadata"):
                result.metadata = {}
            if not hasattr(result, "cached"):
                result.cached = False

            return result

        except Exception as e:
            execution_time_ms = int((time.time() - start_time) * 1000)
            raise AlgorithmExecutionError(
                f"Algorithm '{algorithm.name}' failed: {str(e)}",
                algorithm_name=algorithm.name,
                details={
                    "execution_time_ms": execution_time_ms,
                    "config": config.__dict__,
                    "error_type": type(e).__name__,
                },
            ) from e

    def _get_from_cache(
        self, algorithm_name: str, config: AlgorithmConfig
    ) -> Optional[AlgorithmResult]:
        """
        Get result from cache.

        Args:
            algorithm_name: Name of algorithm
            config: Algorithm configuration

        Returns:
            Cached result or None
        """
        cache_key = self._make_cache_key(algorithm_name, config)
        return self.cache.get(cache_key)

    def _store_in_cache(
        self,
        algorithm_name: str,
        config: AlgorithmConfig,
        result: AlgorithmResult,
        ttl_seconds: int,
    ) -> None:
        """
        Store result in cache.

        Args:
            algorithm_name: Name of algorithm
            config: Algorithm configuration
            result: Result to cache
            ttl_seconds: Time-to-live in seconds
        """
        cache_key = self._make_cache_key(algorithm_name, config)
        self.cache.set(cache_key, result, ttl_seconds)
        # Track cache key for graph invalidation
        if config.graph_id not in self._graph_cache_keys:
            self._graph_cache_keys[config.graph_id] = set()
        self._graph_cache_keys[config.graph_id].add(cache_key)

    def _make_cache_key(self, algorithm_name: str, config: AlgorithmConfig) -> str:
        """
        Create cache key for algorithm result.

        Args:
            algorithm_name: Name of algorithm
            config: Algorithm configuration

        Returns:
            Cache key string
        """
        import hashlib
        import json

        # Create key from algorithm name, graph ID, and parameters
        key_data = {
            "algorithm": algorithm_name,
            "graph_id": str(config.graph_id),
            "parameters": config.parameters,
            "node_filter": str(config.node_filter) if config.node_filter else None,
            "edge_filter": str(config.edge_filter) if config.edge_filter else None,
        }

        key_string = json.dumps(key_data, sort_keys=True)
        key_hash = hashlib.sha256(key_string.encode()).hexdigest()

        return f"{algorithm_name}:{str(config.graph_id)}:{key_hash}"

    def invalidate_graph(self, graph_id: UUID) -> None:
        """
        Invalidate all cached results for a graph.

        Args:
            graph_id: ID of graph to invalidate
        """
        if graph_id in self._graph_cache_keys:
            for cache_key in self._graph_cache_keys[graph_id]:
                self.cache.delete(cache_key)
            del self._graph_cache_keys[graph_id]


__all__ = [
    "CacheConfig",
    "CacheAdapter",
    "AlgorithmExecutor",
]
