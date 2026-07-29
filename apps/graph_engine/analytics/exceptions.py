"""
Common exceptions for graph analytics module.

This module defines custom exceptions for the analytics module.
All exceptions inherit from a common base for consistent error handling.
"""

from __future__ import annotations

from typing import Any, Dict, Optional


class GraphAnalyticsError(Exception):
    """
    Base exception for all graph analytics errors.

    All analytics exceptions should inherit from this base class
    to enable consistent error handling and logging.
    """

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initialize analytics error.

        Args:
            message: Human-readable error message
            error_code: Machine-readable error code
            details: Additional error details
        """
        self.message = message
        self.error_code = error_code or "ANALYTICS_ERROR"
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses."""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details,
        }


class AlgorithmExecutionError(GraphAnalyticsError):
    """
    Raised when an algorithm fails during execution.

    This can happen due to:
    - Algorithm-specific errors
    - Graph structure issues
    - Numerical instability
    - Convergence failures
    """

    def __init__(
        self,
        message: str,
        algorithm_name: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initialize algorithm execution error.

        Args:
            message: Human-readable error message
            algorithm_name: Name of the algorithm that failed
            details: Additional error details
        """
        self.algorithm_name = algorithm_name
        super().__init__(
            message=message,
            error_code="ALGORITHM_EXECUTION_ERROR",
            details=(
                {**details, "algorithm_name": algorithm_name}
                if details
                else {"algorithm_name": algorithm_name}
            ),
        )


class AlgorithmNotFoundError(GraphAnalyticsError):
    """
    Raised when a requested algorithm is not found in the registry.
    """

    def __init__(
        self,
        algorithm_name: str,
        category: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initialize algorithm not found error.

        Args:
            algorithm_name: Name of the algorithm that was not found
            category: Optional category of the algorithm
            details: Additional error details
        """
        self.algorithm_name = algorithm_name
        self.category = category
        error_message = f"Algorithm '{algorithm_name}' not found"
        if category:
            error_message += f" in category '{category}'"

        super().__init__(
            message=error_message,
            error_code="ALGORITHM_NOT_FOUND",
            details=(
                {**details, "algorithm_name": algorithm_name, "category": category}
                if details
                else {"algorithm_name": algorithm_name, "category": category}
            ),
        )


class InvalidGraphError(GraphAnalyticsError):
    """
    Raised when the graph is invalid for algorithm execution.

    This can happen when:
    - Graph is empty
    - Graph has invalid structure
    - Required graph properties are missing
    """

    def __init__(
        self,
        message: str,
        graph_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initialize invalid graph error.

        Args:
            message: Human-readable error message
            graph_id: ID of the invalid graph
            details: Additional error details
        """
        self.graph_id = graph_id
        super().__init__(
            message=message,
            error_code="INVALID_GRAPH_ERROR",
            details=(
                {**details, "graph_id": graph_id} if details else {"graph_id": graph_id}
            ),
        )


class AlgorithmTimeoutError(GraphAnalyticsError):
    """
    Raised when an algorithm execution exceeds the timeout limit.
    """

    def __init__(
        self,
        message: str,
        algorithm_name: str,
        timeout_seconds: int,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initialize algorithm timeout error.

        Args:
            message: Human-readable error message
            algorithm_name: Name of the algorithm that timed out
            timeout_seconds: Timeout limit in seconds
            details: Additional error details
        """
        self.algorithm_name = algorithm_name
        self.timeout_seconds = timeout_seconds
        super().__init__(
            message=message,
            error_code="ALGORITHM_TIMEOUT",
            details=(
                {
                    **details,
                    "algorithm_name": algorithm_name,
                    "timeout_seconds": timeout_seconds,
                }
                if details
                else {
                    "algorithm_name": algorithm_name,
                    "timeout_seconds": timeout_seconds,
                }
            ),
        )


class InvalidConfigError(GraphAnalyticsError):
    """
    Raised when algorithm configuration is invalid.
    """

    def __init__(
        self,
        message: str,
        config_errors: Optional[list[str]] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initialize invalid configuration error.

        Args:
            message: Human-readable error message
            config_errors: List of specific configuration errors
            details: Additional error details
        """
        self.config_errors = config_errors or []
        super().__init__(
            message=message,
            error_code="INVALID_CONFIG_ERROR",
            details=(
                {**details, "config_errors": self.config_errors}
                if details
                else {"config_errors": self.config_errors}
            ),
        )


class CacheError(GraphAnalyticsError):
    """
    Raised when cache operations fail.
    """

    def __init__(
        self,
        message: str,
        cache_key: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initialize cache error.

        Args:
            message: Human-readable error message
            cache_key: Cache key that caused the error
            details: Additional error details
        """
        self.cache_key = cache_key
        super().__init__(
            message=message,
            error_code="CACHE_ERROR",
            details=(
                {**details, "cache_key": cache_key}
                if details
                else {"cache_key": cache_key}
            ),
        )


class FeatureExtractionError(GraphAnalyticsError):
    """
    Raised when feature extraction fails.
    """

    def __init__(
        self,
        message: str,
        feature_name: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initialize feature extraction error.

        Args:
            message: Human-readable error message
            feature_name: Name of the feature that failed to extract
            details: Additional error details
        """
        self.feature_name = feature_name
        super().__init__(
            message=message,
            error_code="FEATURE_EXTRACTION_ERROR",
            details=(
                {**details, "feature_name": feature_name}
                if details
                else {"feature_name": feature_name}
            ),
        )
