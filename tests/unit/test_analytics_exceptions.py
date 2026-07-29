"""
Unit tests for analytics exceptions.

Tests all custom exception classes.
"""

from uuid import uuid4

import pytest

from apps.graph_engine.analytics.exceptions import (
    AlgorithmExecutionError,
    AlgorithmNotFoundError,
    AlgorithmTimeoutError,
    CacheError,
    FeatureExtractionError,
    GraphAnalyticsError,
    InvalidConfigError,
    InvalidGraphError,
)


class TestGraphAnalyticsError:
    """Tests for GraphAnalyticsError base class."""

    def test_basic_error(self):
        """Test creating basic analytics error."""
        error = GraphAnalyticsError("Test error message")

        assert error.message == "Test error message"
        assert error.error_code == "ANALYTICS_ERROR"
        assert error.details == {}
        assert str(error) == "Test error message"

    def test_error_with_code(self):
        """Test error with custom error code."""
        error = GraphAnalyticsError(message="Test error", error_code="CUSTOM_ERROR")

        assert error.error_code == "CUSTOM_ERROR"

    def test_error_with_details(self):
        """Test error with details."""
        details = {"node_id": "test_node", "algorithm": "test"}
        error = GraphAnalyticsError(message="Test error", details=details)

        assert error.details == details

    def test_to_dict(self):
        """Test converting error to dictionary."""
        error = GraphAnalyticsError(
            message="Test error", error_code="TEST_ERROR", details={"key": "value"}
        )

        error_dict = error.to_dict()

        assert error_dict == {
            "error_code": "TEST_ERROR",
            "message": "Test error",
            "details": {"key": "value"},
        }

    def test_to_dict_with_default_values(self):
        """Test converting error to dict with defaults."""
        error = GraphAnalyticsError("Test error")

        error_dict = error.to_dict()

        assert error_dict["error_code"] == "ANALYTICS_ERROR"
        assert error_dict["details"] == {}


class TestAlgorithmExecutionError:
    """Tests for AlgorithmExecutionError."""

    def test_basic_error(self):
        """Test creating algorithm execution error."""
        error = AlgorithmExecutionError(message="Algorithm failed", algorithm_name="test_algo")

        assert error.message == "Algorithm failed"
        assert error.algorithm_name == "test_algo"
        assert error.error_code == "ALGORITHM_EXECUTION_ERROR"
        assert error.details == {"algorithm_name": "test_algo"}

    def test_error_with_details(self):
        """Test error with additional details."""
        error = AlgorithmExecutionError(
            message="Algorithm failed",
            algorithm_name="test_algo",
            details={"iteration": 100, "converged": False},
        )

        assert error.details == {
            "algorithm_name": "test_algo",
            "iteration": 100,
            "converged": False,
        }

    def test_to_dict_includes_algorithm_name(self):
        """Test to_dict includes algorithm name."""
        error = AlgorithmExecutionError(message="Algorithm failed", algorithm_name="test_algo")

        error_dict = error.to_dict()

        assert error_dict["details"]["algorithm_name"] == "test_algo"


class TestAlgorithmNotFoundError:
    """Tests for AlgorithmNotFoundError."""

    def test_basic_error(self):
        """Test creating algorithm not found error."""
        error = AlgorithmNotFoundError(algorithm_name="nonexistent_algo")

        assert "nonexistent_algo" in error.message
        assert error.algorithm_name == "nonexistent_algo"
        assert error.category is None
        assert error.error_code == "ALGORITHM_NOT_FOUND"

    def test_error_with_category(self):
        """Test error with category specified."""
        error = AlgorithmNotFoundError(algorithm_name="nonexistent_algo", category="centrality")

        assert "centrality" in error.message
        assert error.category == "centrality"

    def test_error_with_details(self):
        """Test error with available algorithms in details."""
        error = AlgorithmNotFoundError(
            algorithm_name="nonexistent", details={"available": ["algo1", "algo2"]}
        )

        assert error.details == {
            "algorithm_name": "nonexistent",
            "category": None,
            "available": ["algo1", "algo2"],
        }

    def test_message_format_with_category(self):
        """Test message format includes category when provided."""
        error = AlgorithmNotFoundError(algorithm_name="test_algo", category="centrality")

        message = error.message
        assert "test_algo" in message
        assert "centrality" in message


class TestInvalidGraphError:
    """Tests for InvalidGraphError."""

    def test_basic_error(self):
        """Test creating invalid graph error."""
        error = InvalidGraphError(message="Graph is empty", graph_id=uuid4())

        assert error.message == "Graph is empty"
        assert error.error_code == "INVALID_GRAPH_ERROR"
        assert error.graph_id is not None

    def test_error_without_graph_id(self):
        """Test error without graph ID."""
        error = InvalidGraphError("Invalid structure")

        assert error.graph_id is None
        assert error.details == {"graph_id": None}

    def test_error_with_details(self):
        """Test error with additional details."""
        graph_id = uuid4()
        error = InvalidGraphError(
            message="Graph has cycles", graph_id=graph_id, details={"cycle_count": 5}
        )

        assert error.details == {"graph_id": graph_id, "cycle_count": 5}


class TestAlgorithmTimeoutError:
    """Tests for AlgorithmTimeoutError."""

    def test_basic_error(self):
        """Test creating algorithm timeout error."""
        error = AlgorithmTimeoutError(
            message="Algorithm timed out", algorithm_name="slow_algo", timeout_seconds=300
        )

        assert error.message == "Algorithm timed out"
        assert error.algorithm_name == "slow_algo"
        assert error.timeout_seconds == 300
        assert error.error_code == "ALGORITHM_TIMEOUT"

    def test_to_dict_includes_timeout(self):
        """Test to_dict includes timeout information."""
        error = AlgorithmTimeoutError(message="Timeout", algorithm_name="test", timeout_seconds=60)

        error_dict = error.to_dict()

        assert error_dict["details"]["algorithm_name"] == "test"
        assert error_dict["details"]["timeout_seconds"] == 60


class TestInvalidConfigError:
    """Tests for InvalidConfigError."""

    def test_basic_error(self):
        """Test creating invalid config error."""
        error = InvalidConfigError(message="Configuration is invalid")

        assert error.message == "Configuration is invalid"
        assert error.error_code == "INVALID_CONFIG_ERROR"
        assert error.config_errors == []

    def test_error_with_config_errors(self):
        """Test error with configuration errors."""
        errors = ["Missing parameter: alpha", "Invalid value: beta"]
        error = InvalidConfigError(message="Invalid configuration", config_errors=errors)

        assert error.config_errors == errors
        assert error.details == {"config_errors": errors}

    def test_error_with_details(self):
        """Test error with additional details."""
        error = InvalidConfigError(
            message="Config invalid", config_errors=["error1"], details={"field": "resolution"}
        )

        assert error.details == {"config_errors": ["error1"], "field": "resolution"}


class TestCacheError:
    """Tests for CacheError."""

    def test_basic_error(self):
        """Test creating cache error."""
        error = CacheError("Cache operation failed")

        assert error.message == "Cache operation failed"
        assert error.error_code == "CACHE_ERROR"
        assert error.cache_key is None

    def test_error_with_cache_key(self):
        """Test error with cache key."""
        error = CacheError(message="Key not found", cache_key="test_key")

        assert error.cache_key == "test_key"
        assert error.details == {"cache_key": "test_key"}

    def test_error_with_details(self):
        """Test error with additional details."""
        error = CacheError(message="Cache error", cache_key="my_key", details={"operation": "get"})

        assert error.details == {"cache_key": "my_key", "operation": "get"}


class TestFeatureExtractionError:
    """Tests for FeatureExtractionError."""

    def test_basic_error(self):
        """Test creating feature extraction error."""
        error = FeatureExtractionError("Feature extraction failed")

        assert error.message == "Feature extraction failed"
        assert error.error_code == "FEATURE_EXTRACTION_ERROR"
        assert error.feature_name is None

    def test_error_with_feature_name(self):
        """Test error with feature name."""
        error = FeatureExtractionError(message="Cannot compute feature", feature_name="degree")

        assert error.feature_name == "degree"
        assert error.details == {"feature_name": "degree"}

    def test_error_with_details(self):
        """Test error with additional details."""
        error = FeatureExtractionError(
            message="Feature error", feature_name="betweenness", details={"node_id": "test_node"}
        )

        assert error.details == {"feature_name": "betweenness", "node_id": "test_node"}


class TestExceptionInheritance:
    """Tests for exception inheritance."""

    def test_all_exceptions_inherit_from_base(self):
        """Test that all exceptions inherit from GraphAnalyticsError."""
        exceptions = [
            AlgorithmExecutionError,
            AlgorithmNotFoundError,
            InvalidGraphError,
            AlgorithmTimeoutError,
            InvalidConfigError,
            CacheError,
            FeatureExtractionError,
        ]

        for exc_class in exceptions:
            assert issubclass(
                exc_class, GraphAnalyticsError
            ), f"{exc_class.__name__} does not inherit from GraphAnalyticsError"

    def test_all_exceptions_can_be_caught_as_base(self):
        """Test that all exceptions can be caught as GraphAnalyticsError."""
        errors = [
            AlgorithmExecutionError("test", "algo"),
            AlgorithmNotFoundError("algo"),
            InvalidGraphError("test", uuid4()),
            AlgorithmTimeoutError("test", "algo", 60),
            InvalidConfigError("test"),
            CacheError("test"),
            FeatureExtractionError("test"),
        ]

        for error in errors:
            try:
                raise error
            except GraphAnalyticsError:
                pass  # Expected
            else:
                pytest.fail(f"{type(error).__name__} was not caught as GraphAnalyticsError")

    def test_error_messages_are_descriptive(self):
        """Test that error messages are descriptive."""
        errors = [
            AlgorithmExecutionError("Algorithm execution failed", "test_algo"),
            AlgorithmNotFoundError("Algorithm not found", "test"),
            InvalidGraphError("Graph is invalid", uuid4()),
            AlgorithmTimeoutError("Algorithm timed out", "test", 60),
            InvalidConfigError("Invalid configuration"),
            CacheError("Cache error"),
            FeatureExtractionError("Feature extraction error"),
        ]

        for error in errors:
            assert len(error.message) > 0
            assert isinstance(error.message, str)


class TestExceptionRaising:
    """Tests for raising and catching exceptions."""

    def test_raise_and_catch_specific_exception(self):
        """Test raising and catching specific exception."""
        with pytest.raises(AlgorithmExecutionError) as exc_info:
            raise AlgorithmExecutionError("Test", "algo")

        assert str(exc_info.value) == "Test"
        assert exc_info.value.algorithm_name == "algo"

    def test_catch_as_base_exception(self):
        """Test catching as base exception."""
        try:
            raise AlgorithmExecutionError("Test", "algo")
        except GraphAnalyticsError as e:
            assert e.algorithm_name == "algo"

    def test_error_details_are_preserved(self):
        """Test that error details are preserved."""
        error = AlgorithmExecutionError("Test", "algo", details={"key": "value"})

        assert error.details == {"algorithm_name": "algo", "key": "value"}

    def test_error_code_is_set(self):
        """Test that error codes are set correctly."""
        errors_and_codes = [
            (AlgorithmExecutionError("test", "algo"), "ALGORITHM_EXECUTION_ERROR"),
            (AlgorithmNotFoundError("test"), "ALGORITHM_NOT_FOUND"),
            (InvalidGraphError("test"), "INVALID_GRAPH_ERROR"),
            (AlgorithmTimeoutError("test", "algo", 60), "ALGORITHM_TIMEOUT"),
            (InvalidConfigError("test"), "INVALID_CONFIG_ERROR"),
            (CacheError("test"), "CACHE_ERROR"),
            (FeatureExtractionError("test"), "FEATURE_EXTRACTION_ERROR"),
        ]

        for error, expected_code in errors_and_codes:
            assert error.error_code == expected_code
