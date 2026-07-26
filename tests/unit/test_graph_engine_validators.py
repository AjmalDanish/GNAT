"""
Unit Tests for Graph Engine Validators.

This module contains unit tests for graph engine validators.

Status: Phase 2 - Issue #1
"""

import pytest

from apps.graph_engine.validators import (
    CityValidator,
    CountryValidator,
    TransactionValidator,
)


class TestCountryValidator:
    """Tests for CountryValidator."""

    def test_validate_iso_code_valid(self):
        """Test validation of valid ISO code."""
        CountryValidator.validate_iso_code_2("US")

    def test_validate_iso_code_invalid_length(self):
        """Test validation rejects wrong length ISO codes."""
        with pytest.raises(Exception):
            CountryValidator.validate_iso_code_2("U")
        with pytest.raises(Exception):
            CountryValidator.validate_iso_code_2("USA")

    def test_validate_iso_code_3_valid(self):
        """Test validation of valid ISO-3 code."""
        CountryValidator.validate_iso_code_3("USA")

    def test_validate_iso_code_3_none_allowed(self):
        """Test validation allows None for ISO-3 code."""
        CountryValidator.validate_iso_code_3(None)

    def test_validate_iso_code_3_invalid(self):
        """Test validation rejects invalid ISO-3 codes."""
        from django.core.exceptions import ValidationError

        with pytest.raises(ValidationError):
            CountryValidator.validate_iso_code_3("US")
        with pytest.raises(ValidationError):
            CountryValidator.validate_iso_code_3("USA1")

    def test_validate_country_name_valid(self):
        """Test validation of valid country name."""
        CountryValidator.validate_country_name("United States")

    def test_validate_country_name_invalid(self):
        """Test validation rejects invalid country name."""
        from django.core.exceptions import ValidationError

        with pytest.raises(ValidationError):
            CountryValidator.validate_country_name("")

    def test_validate_latitude_valid(self):
        """Test validation of valid latitude."""
        CountryValidator.validate_latitude(0.0)
        CountryValidator.validate_latitude(45.5)
        CountryValidator.validate_latitude(90.0)
        CountryValidator.validate_latitude(-90.0)

    def test_validate_latitude_none_allowed(self):
        """Test validation allows None for latitude."""
        CountryValidator.validate_latitude(None)

    def test_validate_latitude_invalid(self):
        """Test validation rejects invalid latitude."""
        from django.core.exceptions import ValidationError

        with pytest.raises(ValidationError):
            CountryValidator.validate_latitude(90.1)
        with pytest.raises(ValidationError):
            CountryValidator.validate_latitude(-90.1)

    def test_validate_longitude_valid(self):
        """Test validation of valid longitude."""
        CountryValidator.validate_longitude(0.0)
        CountryValidator.validate_longitude(100.0)
        CountryValidator.validate_longitude(180.0)
        CountryValidator.validate_longitude(-180.0)

    def test_validate_longitude_none_allowed(self):
        """Test validation allows None for longitude."""
        CountryValidator.validate_longitude(None)

    def test_validate_longitude_invalid(self):
        """Test validation rejects invalid longitude."""
        from django.core.exceptions import ValidationError

        with pytest.raises(ValidationError):
            CountryValidator.validate_longitude(180.1)
        with pytest.raises(ValidationError):
            CountryValidator.validate_longitude(-180.1)


class TestCityValidator:
    """Tests for CityValidator."""

    def test_validate_city_name_valid(self):
        """Test validation of valid city name."""
        CityValidator.validate_city_name("New York")
        CityValidator.validate_city_name("東京")

    def test_validate_city_name_invalid(self):
        """Test validation rejects invalid city name."""
        from django.core.exceptions import ValidationError

        with pytest.raises(ValidationError):
            CityValidator.validate_city_name("")

    def test_validate_latitude_valid(self):
        """Test validation of valid latitude."""
        CityValidator.validate_latitude(0.0)
        CityValidator.validate_latitude(45.5)

    def test_validate_latitude_invalid(self):
        """Test validation rejects invalid latitude."""
        from django.core.exceptions import ValidationError

        with pytest.raises(ValidationError):
            CityValidator.validate_latitude(90.1)
        with pytest.raises(ValidationError):
            CityValidator.validate_latitude(-90.1)

    def test_validate_longitude_valid(self):
        """Test validation of valid longitude."""
        CityValidator.validate_longitude(0.0)
        CityValidator.validate_longitude(100.0)

    def test_validate_longitude_invalid(self):
        """Test validation rejects invalid longitude."""
        from django.core.exceptions import ValidationError

        with pytest.raises(ValidationError):
            CityValidator.validate_longitude(180.1)
        with pytest.raises(ValidationError):
            CityValidator.validate_longitude(-180.1)

    def test_validate_population_valid(self):
        """Test validation of valid population."""
        CityValidator.validate_population(0)
        CityValidator.validate_population(1000000)

    def test_validate_population_none_allowed(self):
        """Test validation allows None for population."""
        CityValidator.validate_population(None)

    def test_validate_population_invalid(self):
        """Test validation rejects negative population."""
        from django.core.exceptions import ValidationError

        with pytest.raises(ValidationError):
            CityValidator.validate_population(-1)

    def test_validate_timezone_valid(self):
        """Test validation of valid timezone."""
        CityValidator.validate_timezone(None)  # None is allowed

    def test_validate_timezone_none_allowed(self):
        """Test validation allows None for timezone."""
        CityValidator.validate_timezone(None)

    def test_validate_timezone_invalid(self):
        """Test validation rejects invalid timezone."""
        from django.core.exceptions import ValidationError

        with pytest.raises(ValidationError):
            CityValidator.validate_timezone("")
        with pytest.raises(ValidationError):
            CityValidator.validate_timezone("Invalid/Timezone")


class TestTransactionValidator:
    """Tests for TransactionValidator."""

    def test_validate_packet_count_valid(self):
        """Test validation of valid packet count."""
        TransactionValidator.validate_packet_count(1)
        TransactionValidator.validate_packet_count(1000)

    def test_validate_packet_count_invalid(self):
        """Test validation rejects invalid packet count."""
        from django.core.exceptions import ValidationError

        with pytest.raises(ValidationError):
            TransactionValidator.validate_packet_count(0)
        with pytest.raises(ValidationError):
            TransactionValidator.validate_packet_count(-1)

    def test_validate_bandwidth_valid(self):
        """Test validation of valid bandwidth."""
        TransactionValidator.validate_bandwidth(0.0)
        TransactionValidator.validate_bandwidth(1000.0)

    def test_validate_bandwidth_invalid(self):
        """Test validation rejects invalid bandwidth."""
        from django.core.exceptions import ValidationError

        with pytest.raises(ValidationError):
            TransactionValidator.validate_bandwidth(-1.0)

    def test_validate_latency_valid(self):
        """Test validation of valid latency."""
        TransactionValidator.validate_latency(0.0)
        TransactionValidator.validate_latency(100.5)

    def test_validate_latency_invalid(self):
        """Test validation rejects invalid latency."""
        from django.core.exceptions import ValidationError

        with pytest.raises(ValidationError):
            TransactionValidator.validate_latency(-1.0)

    def test_validate_source_not_equal_destination_valid(self):
        """Test validation passes for different cities."""
        TransactionValidator.validate_source_not_equal_destination("city1", "city2")

    def test_validate_source_not_equal_destination_invalid(self):
        """Test validation fails for same city."""
        from django.core.exceptions import ValidationError

        with pytest.raises(ValidationError):
            TransactionValidator.validate_source_not_equal_destination("city1", "city1")
