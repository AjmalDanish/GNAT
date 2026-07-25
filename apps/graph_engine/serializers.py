"""
Serializers for Graph Engine API.

This module provides DRF serializers for graph engine models.

Architecture:
- Django REST Framework
- Clean Architecture: Presentation Layer
- Validation via validators module

Status: Phase 2 - Issue #1
"""
from rest_framework import serializers

from .models import City, Country, Dataset, Transaction


class CountrySerializer(serializers.ModelSerializer):
    """Serializer for Country model."""

    class Meta:
        model = Country
        fields = [
            "id",
            "iso_code",
            "iso_code_3",
            "country_name",
            "continent",
            "latitude",
            "longitude",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class CitySerializer(serializers.ModelSerializer):
    """Serializer for City model."""

    country = CountrySerializer(read_only=True)
    country_id = serializers.UUIDField(write_only=True)
    coordinates = serializers.SerializerMethodField()

    class Meta:
        model = City
        fields = [
            "id",
            "country",
            "country_id",
            "city_name",
            "latitude",
            "longitude",
            "population",
            "timezone",
            "coordinates",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_coordinates(self, obj: City) -> tuple[float, float]:
        """Get city coordinates."""
        return (obj.latitude, obj.longitude)


class CityListSerializer(serializers.ModelSerializer):
    """Simplified serializer for city list views."""

    country_name = serializers.CharField(source="country.country_name", read_only=True)

    class Meta:
        model = City
        fields = ["id", "city_name", "country_name", "latitude", "longitude", "population"]


class DatasetSerializer(serializers.ModelSerializer):
    """Serializer for Dataset model."""

    created_by_username = serializers.CharField(source="created_by.username", read_only=True, allow_null=True)

    class Meta:
        model = Dataset
        fields = [
            "id",
            "dataset_name",
            "version",
            "description",
            "source",
            "created_by",
            "created_by_username",
            "created_at",
            "status",
            "record_count",
            "configuration",
            "random_seed",
            "statistics",
            "checksum",
        ]
        read_only_fields = ["id", "created_at", "checksum"]


class DatasetCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating datasets."""

    class Meta:
        model = Dataset
        fields = [
            "dataset_name",
            "version",
            "description",
            "source",
            "configuration",
            "random_seed",
        ]

    def validate_version(self, value: str) -> str:
        """Validate version format."""
        # Basic semantic versioning validation
        parts = value.split(".")
        if len(parts) != 3 or not all(part.isdigit() for part in parts):
            raise serializers.ValidationError(
                "Version must follow semantic versioning (e.g., '1.0.0')"
            )
        return value


class TransactionSerializer(serializers.ModelSerializer):
    """Serializer for Transaction model."""

    source_city_name = serializers.CharField(source="source_city.city_name", read_only=True)
    destination_city_name = serializers.CharField(source="destination_city.city_name", read_only=True)
    source_country = serializers.CharField(source="source_city.country.country_name", read_only=True)
    destination_country = serializers.CharField(source="destination_city.country.country_name", read_only=True)

    class Meta:
        model = Transaction
        fields = [
            "id",
            "dataset",
            "source_city",
            "destination_city",
            "source_city_name",
            "destination_city_name",
            "source_country",
            "destination_country",
            "packet_count",
            "packet_size",
            "bandwidth",
            "latency",
            "duration",
            "protocol",
            "timestamp",
            "is_anomaly",
            "connection_type",
            "encryption",
            "risk_label",
        ]
        read_only_fields = ["id", "timestamp"]


class TransactionListSerializer(serializers.ModelSerializer):
    """Simplified serializer for transaction list views."""

    class Meta:
        model = Transaction
        fields = [
            "id",
            "source_city_name",
            "destination_city_name",
            "protocol",
            "bandwidth",
            "latency",
            "is_anomaly",
            "risk_label",
            "timestamp",
        ]


class GenerateDatasetSerializer(serializers.Serializer):
    """Serializer for dataset generation request."""

    dataset_name = serializers.CharField(max_length=255)
    version = serializers.CharField(max_length=20, default="1.0.0")
    description = serializers.CharField(required=False, allow_blank=True)
    num_transactions = serializers.IntegerField(min_value=1, max_value=1000000, default=1000)
    time_window_hours = serializers.IntegerField(min_value=1, max_value=168, default=24)
    pattern = serializers.ChoiceField(
        choices=["random", "business", "regional", "international", "hub_based"],
        default="random",
    )
    anomaly_percentage = serializers.FloatField(min_value=0.0, max_value=1.0, default=0.05)
    random_seed = serializers.IntegerField(required=False, allow_null=True)
    min_population = serializers.IntegerField(required=False, allow_null=True)
    continents = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_null=True,
    )


class DatasetStatisticsSerializer(serializers.Serializer):
    """Serializer for dataset statistics."""

    total_transactions = serializers.IntegerField()
    anomaly_count = serializers.IntegerField()
    anomaly_percentage = serializers.FloatField()
    total_bandwidth = serializers.FloatField()
    average_latency = serializers.FloatField()