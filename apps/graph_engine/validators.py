"""
Validators for Graph Engine.

This module contains validation logic for graph engine data.

Architecture:
- Clean Architecture: Domain Layer
- Pure validation logic
- No external dependencies

Status: Phase 2 - Issue #1
"""

import re
from decimal import Decimal, InvalidOperation
from typing import Any, Optional


class ValidationError(Exception):
    """Custom validation exception."""

    def __init__(self, message: str, field: Optional[str] = None) -> None:
        """Initialize validation error."""
        self.message = message
        self.field = field
        super().__init__(message)


class CityValidator:
    """
    Validator for city data.

    Validates geographic coordinates, population, and other city attributes.
    """

    @staticmethod
    def validate_latitude(latitude: Any) -> float:
        """
        Validate latitude coordinate.

        Args:
            latitude: Latitude value to validate.

        Returns:
            Validated latitude as float.

        Raises:
            ValidationError: If latitude is invalid.
        """
        try:
            lat = float(latitude)
        except (ValueError, TypeError) as e:
            raise ValidationError(
                f"Latitude must be a number, got {type(latitude).__name__}: {latitude}", "latitude"
            ) from e

        if not -90 <= lat <= 90:
            raise ValidationError(f"Latitude must be between -90 and 90, got {lat}", "latitude")

        return lat

    @staticmethod
    def validate_longitude(longitude: Any) -> float:
        """
        Validate longitude coordinate.

        Args:
            longitude: Longitude value to validate.

        Returns:
            Validated longitude as float.

        Raises:
            ValidationError: If longitude is invalid.
        """
        try:
            lon = float(longitude)
        except (ValueError, TypeError) as e:
            raise ValidationError(
                f"Longitude must be a number, got {type(longitude).__name__}: {longitude}",
                "longitude",
            ) from e

        if not -180 <= lon <= 180:
            raise ValidationError(f"Longitude must be between -180 and 180, got {lon}", "longitude")

        return lon

    @staticmethod
    def validate_population(population: Any) -> Optional[int]:
        """
        Validate population value.

        Args:
            population: Population value to validate.

        Returns:
            Validated population as int, or None if empty.

        Raises:
            ValidationError: If population is invalid.
        """
        if population is None or population == "":
            return None

        try:
            pop = int(population)
        except (ValueError, TypeError) as e:
            raise ValidationError(
                f"Population must be an integer, got {type(population).__name__}: {population}",
                "population",
            ) from e

        if pop < 0:
            raise ValidationError(f"Population must be non-negative, got {pop}", "population")

        return pop

    @staticmethod
    def validate_timezone(timezone: Any) -> Optional[str]:
        """
        Validate timezone identifier.

        Args:
            timezone: Timezone identifier to validate.

        Returns:
            Validated timezone string, or None if empty.

        Raises:
            ValidationError: If timezone is invalid.
        """
        if timezone is None or timezone == "":
            return None

        if not isinstance(timezone, str):
            raise ValidationError(
                f"Timezone must be a string, got {type(timezone).__name__}", "timezone"
            )

        # Basic timezone format validation (e.g., "America/New_York")
        pattern = r"^[A-Za-z]+/[A-Za-z_]+$"
        if not re.match(pattern, timezone):
            raise ValidationError(
                f"Invalid timezone format: {timezone}. Expected format: 'Region/City'", "timezone"
            )

        return timezone

    @staticmethod
    def validate_city_name(city_name: Any) -> str:
        """
        Validate city name.

        Args:
            city_name: City name to validate.

        Returns:
            Validated city name string.

        Raises:
            ValidationError: If city name is invalid.
        """
        if not city_name:
            raise ValidationError("City name cannot be empty", "city_name")

        if not isinstance(city_name, str):
            raise ValidationError(
                f"City name must be a string, got {type(city_name).__name__}", "city_name"
            )

        # Remove extra whitespace
        city_name = city_name.strip()

        if len(city_name) < 2:
            raise ValidationError(
                f"City name must be at least 2 characters, got '{city_name}'", "city_name"
            )

        if len(city_name) > 100:
            raise ValidationError(
                f"City name cannot exceed 100 characters, got {len(city_name)}", "city_name"
            )

        return city_name

    @classmethod
    def validate_city_data(cls, city_data: dict[str, Any]) -> dict[str, Any]:
        """
        Validate complete city data dictionary.

        Args:
            city_data: Dictionary containing city data.

        Returns:
            Validated and cleaned city data.

        Raises:
            ValidationError: If any field is invalid.
        """
        validated = {}

        if "city_name" in city_data:
            validated["city_name"] = cls.validate_city_name(city_data["city_name"])

        if "latitude" in city_data:
            validated["latitude"] = cls.validate_latitude(city_data["latitude"])

        if "longitude" in city_data:
            validated["longitude"] = cls.validate_longitude(city_data["longitude"])

        if "population" in city_data:
            validated["population"] = cls.validate_population(city_data["population"])

        if "timezone" in city_data:
            validated["timezone"] = cls.validate_timezone(city_data["timezone"])

        return validated


class CountryValidator:
    """
    Validator for country data.

    Validates ISO codes, country names, and geographic coordinates.
    """

    @staticmethod
    def validate_iso_code(iso_code: Any) -> str:
        """
        Validate ISO 3166-1 alpha-2 country code.

        Args:
            iso_code: ISO code to validate.

        Returns:
            Validated ISO code string (uppercase).

        Raises:
            ValidationError: If ISO code is invalid.
        """
        if not iso_code:
            raise ValidationError("ISO code cannot be empty", "iso_code")

        if not isinstance(iso_code, str):
            raise ValidationError(
                f"ISO code must be a string, got {type(iso_code).__name__}", "iso_code"
            )

        iso_code = iso_code.strip().upper()

        if len(iso_code) != 2:
            raise ValidationError(
                f"ISO code must be exactly 2 characters, got {len(iso_code)}", "iso_code"
            )

        if not iso_code.isalpha():
            raise ValidationError(
                f"ISO code must contain only letters, got '{iso_code}'", "iso_code"
            )

        return iso_code

    @staticmethod
    def validate_iso_code_3(iso_code_3: Any) -> Optional[str]:
        """
        Validate ISO 3166-1 alpha-3 country code.

        Args:
            iso_code_3: ISO 3-letter code to validate.

        Returns:
            Validated ISO 3-letter code string (uppercase), or None if empty.

        Raises:
            ValidationError: If ISO code is invalid.
        """
        if iso_code_3 is None or iso_code_3 == "":
            return None

        if not isinstance(iso_code_3, str):
            raise ValidationError(
                f"ISO 3-letter code must be a string, got {type(iso_code_3).__name__}", "iso_code_3"
            )

        iso_code_3 = iso_code_3.strip().upper()

        if len(iso_code_3) != 3:
            raise ValidationError(
                f"ISO 3-letter code must be exactly 3 characters, got {len(iso_code_3)}",
                "iso_code_3",
            )

        if not iso_code_3.isalpha():
            raise ValidationError(
                f"ISO 3-letter code must contain only letters, got '{iso_code_3}'", "iso_code_3"
            )

        return iso_code_3

    @staticmethod
    def validate_country_name(country_name: Any) -> str:
        """
        Validate country name.

        Args:
            country_name: Country name to validate.

        Returns:
            Validated country name string.

        Raises:
            ValidationError: If country name is invalid.
        """
        if not country_name:
            raise ValidationError("Country name cannot be empty", "country_name")

        if not isinstance(country_name, str):
            raise ValidationError(
                f"Country name must be a string, got {type(country_name).__name__}", "country_name"
            )

        # Remove extra whitespace and title case
        country_name = " ".join(country_name.strip().split())

        if len(country_name) < 2:
            raise ValidationError(
                f"Country name must be at least 2 characters, got '{country_name}'", "country_name"
            )

        if len(country_name) > 100:
            raise ValidationError(
                f"Country name cannot exceed 100 characters, got {len(country_name)}",
                "country_name",
            )

        return country_name

    @classmethod
    def validate_country_data(cls, country_data: dict[str, Any]) -> dict[str, Any]:
        """
        Validate complete country data dictionary.

        Args:
            country_data: Dictionary containing country data.

        Returns:
            Validated and cleaned country data.

        Raises:
            ValidationError: If any field is invalid.
        """
        validated = {}

        if "iso_code" in country_data:
            validated["iso_code"] = cls.validate_iso_code(country_data["iso_code"])

        if "iso_code_3" in country_data:
            validated["iso_code_3"] = cls.validate_iso_code_3(country_data["iso_code_3"])

        if "country_name" in country_data:
            validated["country_name"] = cls.validate_country_name(country_data["country_name"])

        if "latitude" in country_data:
            validated["latitude"] = CityValidator.validate_latitude(country_data["latitude"])

        if "longitude" in country_data:
            validated["longitude"] = CityValidator.validate_longitude(country_data["longitude"])

        return validated


class TransactionValidator:
    """
    Validator for transaction data.

    Validates network traffic transaction attributes.
    """

    @staticmethod
    def validate_packet_count(packet_count: Any) -> int:
        """
        Validate packet count.

        Args:
            packet_count: Packet count to validate.

        Returns:
            Validated packet count as int.

        Raises:
            ValidationError: If packet count is invalid.
        """
        try:
            count = int(packet_count)
        except (ValueError, TypeError) as e:
            raise ValidationError(
                f"Packet count must be an integer, got {type(packet_count).__name__}",
                "packet_count",
            ) from e

        if count <= 0:
            raise ValidationError(f"Packet count must be positive, got {count}", "packet_count")

        return count

    @staticmethod
    def validate_bandwidth(bandwidth: Any) -> float:
        """
        Validate bandwidth value.

        Args:
            bandwidth: Bandwidth value to validate (bytes per second).

        Returns:
            Validated bandwidth as float.

        Raises:
            ValidationError: If bandwidth is invalid.
        """
        try:
            bw = float(bandwidth)
        except (ValueError, TypeError) as e:
            raise ValidationError(
                f"Bandwidth must be a number, got {type(bandwidth).__name__}", "bandwidth"
            ) from e

        if bw < 0:
            raise ValidationError(f"Bandwidth must be non-negative, got {bw}", "bandwidth")

        return bw

    @staticmethod
    def validate_latency(latency: Any) -> float:
        """
        Validate latency value.

        Args:
            latency: Latency value to validate (milliseconds).

        Returns:
            Validated latency as float.

        Raises:
            ValidationError: If latency is invalid.
        """
        try:
            lat = float(latency)
        except (ValueError, TypeError) as e:
            raise ValidationError(
                f"Latency must be a number, got {type(latency).__name__}", "latency"
            ) from e

        if lat < 0:
            raise ValidationError(f"Latency must be non-negative, got {lat}", "latency")

        return lat

    @classmethod
    def validate_transaction_data(cls, transaction_data: dict[str, Any]) -> dict[str, Any]:
        """
        Validate complete transaction data dictionary.

        Args:
            transaction_data: Dictionary containing transaction data.

        Returns:
            Validated and cleaned transaction data.

        Raises:
            ValidationError: If any field is invalid.
        """
        validated = {}

        if "packet_count" in transaction_data:
            validated["packet_count"] = cls.validate_packet_count(transaction_data["packet_count"])

        if "bandwidth" in transaction_data:
            validated["bandwidth"] = cls.validate_bandwidth(transaction_data["bandwidth"])

        if "latency" in transaction_data:
            validated["latency"] = cls.validate_latency(transaction_data["latency"])

        if "packet_size" in transaction_data:
            try:
                validated["packet_size"] = int(transaction_data["packet_size"])
            except (ValueError, TypeError):
                validated["packet_size"] = 1500  # Default MTU size

        return validated
