"""
Validators for Graph Engine.

This module provides data validation logic for graph engine models.

Architecture:
- Clean Architecture: Application Layer
- Input validation before persistence
- Geographic coordinate validation
- Network constraint validation

Status: Phase 2 - Issue #1
"""

import re
from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class CountryValidator:
    """Validator for Country model data."""

    ISO2_PATTERN = re.compile(r"^[A-Z]{2}$")
    ISO3_PATTERN = re.compile(r"^[A-Z]{3}$")

    @staticmethod
    def validate_iso_code_2(code: str) -> None:
        """Validate 2-letter ISO code."""
        if not code or len(code) != 2:
            raise ValidationError(
                {"iso_code": _("ISO code must be exactly 2 characters.")}
            )
        if not code.isupper():
            raise ValidationError(
                {"iso_code": _("ISO code must be uppercase letters.")}
            )
        if not CountryValidator.ISO2_PATTERN.match(code):
            raise ValidationError(
                {"iso_code": _("Invalid ISO 3166-1 alpha-2 code format.")}
            )

    @staticmethod
    def validate_iso_code_3(code: str | None) -> None:
        """Validate 3-letter ISO code."""
        if code is not None:
            if len(code) != 3:
                raise ValidationError(
                    {"iso_code_3": _("ISO 3 code must be exactly 3 characters.")}
                )
            if not code.isupper():
                raise ValidationError(
                    {"iso_code_3": _("ISO 3 code must be uppercase letters.")}
                )
            if not CountryValidator.ISO3_PATTERN.match(code):
                raise ValidationError(
                    {"iso_code_3": _("Invalid ISO 3166-1 alpha-3 code format.")}
                )

    @staticmethod
    def validate_country_name(name: str) -> None:
        """Validate country name."""
        if not name or len(name.strip()) == 0:
            raise ValidationError({"country_name": _("Country name cannot be empty.")})
        if len(name) > 100:
            raise ValidationError(
                {"country_name": _("Country name cannot exceed 100 characters.")}
            )

    @staticmethod
    def validate_latitude(latitude: float | None) -> None:
        """Validate latitude coordinate."""
        if latitude is not None:
            if not -90 <= latitude <= 90:
                raise ValidationError(
                    {"latitude": _("Latitude must be between -90 and 90 degrees.")}
                )

    @staticmethod
    def validate_longitude(longitude: float | None) -> None:
        """Validate longitude coordinate."""
        if longitude is not None:
            if not -180 <= longitude <= 180:
                raise ValidationError(
                    {"longitude": _("Longitude must be between -180 and 180 degrees.")}
                )


class CityValidator:
    """Validator for City model data."""

    @staticmethod
    def validate_city_name(name: str) -> None:
        """Validate city name."""
        if not name or len(name.strip()) == 0:
            raise ValidationError({"city_name": _("City name cannot be empty.")})
        if len(name) > 100:
            raise ValidationError(
                {"city_name": _("City name cannot exceed 100 characters.")}
            )

    @staticmethod
    def validate_latitude(latitude: float) -> None:
        """Validate latitude coordinate."""
        if not -90 <= latitude <= 90:
            raise ValidationError(
                {"latitude": _("Latitude must be between -90 and 90 degrees.")}
            )

    @staticmethod
    def validate_longitude(longitude: float) -> None:
        """Validate longitude coordinate."""
        if not -180 <= longitude <= 180:
            raise ValidationError(
                {"longitude": _("Longitude must be between -180 and 180 degrees.")}
            )

    @staticmethod
    def validate_population(population: int | None) -> None:
        """Validate population."""
        if population is not None:
            if population < 0:
                raise ValidationError(
                    {"population": _("Population cannot be negative.")}
                )

    @staticmethod
    def validate_timezone(tz: str | None) -> None:
        """Validate timezone identifier."""
        if tz is not None and len(tz) > 0:
            # Basic validation - could use zoneinfo for more thorough checks
            if not re.match(r"^[A-Za-z_]+/[A-Za-z_]+/[A-Za-z_]+$", tz):
                raise ValidationError({"timezone": _("Invalid timezone format.")})


class TransactionValidator:
    """Validator for Transaction model data."""

    @staticmethod
    def validate_packet_count(count: int) -> None:
        """Validate packet count."""
        if count <= 0:
            raise ValidationError(
                {"packet_count": _("Packet count must be a positive integer.")}
            )

    @staticmethod
    def validate_bandwidth(bandwidth: float) -> None:
        """Validate bandwidth."""
        try:
            bw = Decimal(str(bandwidth))
            if bw < 0:
                raise ValidationError({"bandwidth": _("Bandwidth cannot be negative.")})
        except (InvalidOperation, ValueError):
            raise ValidationError({"bandwidth": _("Bandwidth must be a valid number.")})

    @staticmethod
    def validate_latency(latency: float) -> None:
        """Validate latency."""
        try:
            lat = Decimal(str(latency))
            if lat < 0:
                raise ValidationError({"latency": _("Latency cannot be negative.")})
        except (InvalidOperation, ValueError):
            raise ValidationError({"latency": _("Latency must be a valid number.")})

    @staticmethod
    def validate_source_not_equal_destination(
        source_id: str, destination_id: str
    ) -> None:
        """Validate source and destination are different cities."""
        if source_id == destination_id:
            raise ValidationError(
                {
                    "destination_city": _(
                        "Source and destination cannot be the same city."
                    )
                }
            )
