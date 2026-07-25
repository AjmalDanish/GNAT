"""
Country Model for GNAT.

This module defines the Country model which stores geographic information
about countries worldwide. It serves as a reference for City records.

Architecture:
- Follows Django ORM conventions
- Uses UUID primary key
- Supports geographic queries
- Clean Architecture: Domain Layer

Status: Phase 2 - Issue #1
"""

import uuid
from typing import Any

from django.contrib.gis.db import models as gis_models
from django.db import models
from django.utils.translation import gettext_lazy as _


class Country(gis_models.Model):
    """
    Country model representing countries worldwide.

    This model stores geographic and administrative information about countries.
    Cities are associated with countries via foreign key relationships.

    Attributes:
        id: UUID primary key
        iso_code: ISO 3166-1 alpha-2 code (e.g., 'US', 'UK', 'JP')
        iso_code_3: ISO 3166-1 alpha-3 code (e.g., 'USA', 'GBR', 'JPN')
        country_name: Full country name
        continent: Continent name
        latitude: Approximate center latitude
        longitude: Approximate center longitude
        created_at: Timestamp when record was created
        updated_at: Timestamp when record was last updated

    Relationships:
        cities: Reverse relationship to City model

    Indexes:
        - country_name
        - iso_code
        - continent
    """

    class Continent(models.TextChoices):
        """Continent enumeration for type safety."""

        AFRICA = "AF", _("Africa")
        ASIA = "AS", _("Asia")
        EUROPE = "EU", _("Europe")
        NORTH_AMERICA = "NA", _("North America")
        SOUTH_AMERICA = "SA", _("South America")
        OCEANIA = "OC", _("Oceania")
        ANTARCTICA = "AN", _("Antarctica")

    # Primary Key
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text=_("Unique identifier for the country"),
    )

    # Identification
    iso_code = models.CharField(
        max_length=2,
        unique=True,
        db_index=True,
        help_text=_("ISO 3166-1 alpha-2 country code"),
    )

    iso_code_3 = models.CharField(
        max_length=3,
        unique=True,
        null=True,
        blank=True,
        help_text=_("ISO 3166-1 alpha-3 country code"),
    )

    country_name = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text=_("Full country name"),
    )

    # Geographic Information
    continent = models.CharField(
        max_length=2,
        choices=Continent.choices,
        db_index=True,
        help_text=_("Continent where the country is located"),
    )

    latitude = models.FloatField(
        null=True,
        blank=True,
        help_text=_("Approximate center latitude coordinate"),
    )

    longitude = models.FloatField(
        null=True,
        blank=True,
        help_text=_("Approximate center longitude coordinate"),
    )

    # Metadata
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_("Timestamp when the country record was created"),
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text=_("Timestamp when the country record was last updated"),
    )

    class Meta:
        """Meta configuration for Country model."""

        db_table = "country"
        verbose_name = _("Country")
        verbose_name_plural = _("Countries")
        ordering = ["country_name"]
        indexes = [
            models.Index(fields=["country_name"]),
            models.Index(fields=["iso_code"]),
            models.Index(fields=["continent"]),
            models.Index(fields=["iso_code", "country_name"]),
        ]

    def __str__(self) -> str:
        """String representation of Country."""
        return f"{self.country_name} ({self.iso_code})"

    def get_absolute_url(self) -> str:
        """Get absolute URL for country detail view."""
        from django.urls import reverse

        return reverse("graph_engine:country_detail", kwargs={"pk": self.pk})


class City(gis_models.Model):
    """
    City model representing cities worldwide.

    This model stores geographic and demographic information about cities.
    Cities are associated with countries and serve as nodes in network graphs.

    Attributes:
        id: UUID primary key
        country: Foreign key to Country
        city_name: Name of the city
        latitude: Geographic latitude coordinate
        longitude: Geographic longitude coordinate
        population: City population
        timezone: Timezone identifier
        created_at: Timestamp when record was created
        updated_at: Timestamp when record was last updated

    Relationships:
        country: Many-to-one relationship with Country

    Indexes:
        - country_id
        - city_name
    """

    # Primary Key
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text=_("Unique identifier for the city"),
    )

    # Foreign Key to Country
    country = models.ForeignKey(
        "Country",
        on_delete=models.CASCADE,
        related_name="cities",
        db_index=True,
        help_text=_("Country where the city is located"),
    )

    # Identification
    city_name = models.CharField(
        max_length=100,
        db_index=True,
        help_text=_("Name of the city"),
    )

    # Geographic Information
    latitude = models.FloatField(
        db_index=True,
        help_text=_("Geographic latitude coordinate in decimal degrees"),
    )

    longitude = models.FloatField(
        db_index=True,
        help_text=_("Geographic longitude coordinate in decimal degrees"),
    )

    # Demographic Information
    population = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text=_("City population"),
    )

    # Timezone
    timezone = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text=_("Timezone identifier (e.g., 'America/New_York')"),
    )

    # Metadata
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_("Timestamp when the city record was created"),
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text=_("Timestamp when the city record was last updated"),
    )

    class Meta:
        """Meta configuration for City model."""

        db_table = "city"
        verbose_name = _("City")
        verbose_name_plural = _("Cities")
        ordering = ["city_name"]
        indexes = [
            models.Index(fields=["country"]),
            models.Index(fields=["city_name"]),
            models.Index(fields=["latitude", "longitude"]),
            models.Index(fields=["country", "city_name"]),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(latitude__gte=-90) & models.Q(latitude__lte=90),
                name="valid_latitude",
            ),
            models.CheckConstraint(
                check=models.Q(longitude__gte=-180) & models.Q(longitude__lte=180),
                name="valid_longitude",
            ),
        ]

    def __str__(self) -> str:
        """String representation of City."""
        return f"{self.city_name}, {self.country.country_name}"

    def get_absolute_url(self) -> str:
        """Get absolute URL for city detail view."""
        from django.urls import reverse

        return reverse("graph_engine:city_detail", kwargs={"pk": self.pk})

    @property
    def coordinates(self) -> tuple[float, float]:
        """Get city coordinates as (latitude, longitude) tuple."""
        return (self.latitude, self.longitude)


class Dataset(models.Model):
    """
    Dataset model for synthetic data metadata.

    This model stores metadata about synthetic datasets generated
    by the Synthetic Data Engine. It tracks versioning, configuration,
    and statistics for each generated dataset.

    Attributes:
        id: UUID primary key
        dataset_name: Name of the dataset
        description: Description of the dataset
        source: Source of the data
        version: Dataset version
        created_by: User who created the dataset
        created_at: Timestamp when dataset was created
        status: Dataset status
        record_count: Number of records in the dataset
        configuration: JSON configuration used for generation
        random_seed: Random seed used for generation
        statistics: JSON statistics about the dataset
        checksum: Checksum for data integrity

    Relationships:
        transactions: Reverse relationship to Transaction model

    Indexes:
        - version
        - status
    """

    class DatasetStatus(models.TextChoices):
        """Dataset status enumeration."""

        PENDING = "PENDING", _("Pending")
        GENERATING = "GENERATING", _("Generating")
        COMPLETED = "COMPLETED", _("Completed")
        FAILED = "FAILED", _("Failed")
        ARCHIVED = "ARCHIVED", _("Archived")

    # Primary Key
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text=_("Unique identifier for the dataset"),
    )

    # Identification
    dataset_name = models.CharField(
        max_length=255,
        db_index=True,
        help_text=_("Name of the dataset"),
    )

    description = models.TextField(
        blank=True,
        help_text=_("Description of the dataset purpose and contents"),
    )

    source = models.CharField(
        max_length=100,
        default="synthetic",
        help_text=_("Source of the data"),
    )

    version = models.CharField(
        max_length=20,
        db_index=True,
        help_text=_("Dataset version following semantic versioning"),
    )

    # User Tracking
    created_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="datasets",
        help_text=_("User who created the dataset"),
    )

    # Metadata
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_("Timestamp when the dataset was created"),
    )

    status = models.CharField(
        max_length=20,
        choices=DatasetStatus.choices,
        db_index=True,
        default=DatasetStatus.PENDING,
        help_text=_("Current status of the dataset"),
    )

    record_count = models.PositiveIntegerField(
        default=0,
        help_text=_("Number of records in the dataset"),
    )

    # Configuration (stored as JSON)
    configuration = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Configuration used for dataset generation"),
    )

    random_seed = models.IntegerField(
        null=True,
        blank=True,
        help_text=_("Random seed used for reproducibility"),
    )

    statistics = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Statistics about the dataset content"),
    )

    checksum = models.CharField(
        max_length=64,
        blank=True,
        help_text=_("Checksum for data integrity verification"),
    )

    class Meta:
        """Meta configuration for Dataset model."""

        db_table = "dataset"
        verbose_name = _("Dataset")
        verbose_name_plural = _("Datasets")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["version"]),
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["status", "created_at"]),
        ]
        unique_together = [["dataset_name", "version"]]

    def __str__(self) -> str:
        """String representation of Dataset."""
        return f"{self.dataset_name} v{self.version}"

    def get_absolute_url(self) -> str:
        """Get absolute URL for dataset detail view."""
        from django.urls import reverse

        return reverse("graph_engine:dataset_detail", kwargs={"pk": self.pk})


class Transaction(models.Model):
    """
    Transaction model representing synthetic network traffic.

    This model stores individual network communication transactions between cities.
    Each transaction represents a network flow with various metrics and attributes.

    Attributes:
        id: UUID primary key
        dataset: Foreign key to Dataset
        source_city: Foreign key to source City
        destination_city: Foreign key to destination City
        packet_count: Number of packets in the transaction
        latency: Network latency in milliseconds
        bandwidth: Bandwidth used in bytes per second
        protocol: Network protocol used
        timestamp: Timestamp of the transaction
        is_anomaly: Whether this transaction is an anomaly
        connection_type: Type of connection
        encryption: Whether encryption was used
        risk_label: Risk classification label

    Relationships:
        dataset: Many-to-one relationship with Dataset
        source_city: Many-to-one relationship with City
        destination_city: Many-to-one relationship with City

    Indexes:
        - dataset_id
        - timestamp
        - source_city
        - destination_city
    """

    class Protocol(models.TextChoices):
        """Network protocol enumeration."""

        HTTP = "HTTP", _("HTTP")
        HTTPS = "HTTPS", _("HTTPS")
        SSH = "SSH", _("SSH")
        FTP = "FTP", _("FTP")
        SMTP = "SMTP", _("SMTP")
        DNS = "DNS", _("DNS")
        TCP = "TCP", _("TCP")
        UDP = "UDP", _("UDP")
        ICMP = "ICMP", _("ICMP")
        MQTT = "MQTT", _("MQTT")
        WEBSOCKET = "WEBSOCKET", _("WebSocket")

    class ConnectionType(models.TextChoices):
        """Connection type enumeration."""

        PEER_TO_PEER = "P2P", _("Peer-to-Peer")
        CLIENT_SERVER = "CLIENT_SERVER", _("Client-Server")
        HYBRID = "HYBRID", _("Hybrid")

    class RiskLabel(models.TextChoices):
        """Risk label enumeration."""

        NORMAL = "NORMAL", _("Normal")
        LOW = "LOW", _("Low Risk")
        MEDIUM = "MEDIUM", _("Medium Risk")
        HIGH = "HIGH", _("High Risk")
        CRITICAL = "CRITICAL", _("Critical")

    # Primary Key
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text=_("Unique identifier for the transaction"),
    )

    # Foreign Keys
    dataset = models.ForeignKey(
        "Dataset",
        on_delete=models.CASCADE,
        related_name="transactions",
        db_index=True,
        help_text=_("Dataset this transaction belongs to"),
    )

    source_city = models.ForeignKey(
        "City",
        on_delete=models.CASCADE,
        related_name="outgoing_transactions",
        db_index=True,
        help_text=_("Source city of the transaction"),
    )

    destination_city = models.ForeignKey(
        "City",
        on_delete=models.CASCADE,
        related_name="incoming_transactions",
        db_index=True,
        help_text=_("Destination city of the transaction"),
    )

    # Traffic Metrics
    packet_count = models.PositiveIntegerField(
        help_text=_("Number of packets in the transaction"),
    )

    packet_size = models.PositiveIntegerField(
        default=1500,
        help_text=_("Average packet size in bytes"),
    )

    bandwidth = models.FloatField(
        help_text=_("Bandwidth used in bytes per second"),
    )

    latency = models.FloatField(
        help_text=_("Network latency in milliseconds"),
    )

    duration = models.FloatField(
        default=0.0,
        help_text=_("Connection duration in seconds"),
    )

    # Classification
    protocol = models.CharField(
        max_length=10,
        choices=Protocol.choices,
        default=Protocol.HTTPS,
        help_text=_("Network protocol used"),
    )

    timestamp = models.DateTimeField(
        db_index=True,
        help_text=_("Timestamp of the transaction"),
    )

    is_anomaly = models.BooleanField(
        default=False,
        db_index=True,
        help_text=_("Whether this transaction is an anomaly"),
    )

    connection_type = models.CharField(
        max_length=20,
        choices=ConnectionType.choices,
        default=ConnectionType.CLIENT_SERVER,
        help_text=_("Type of connection"),
    )

    encryption = models.BooleanField(
        default=False,
        help_text=_("Whether encryption was used"),
    )

    risk_label = models.CharField(
        max_length=10,
        choices=RiskLabel.choices,
        default=RiskLabel.NORMAL,
        help_text=_("Risk classification label"),
    )

    class Meta:
        """Meta configuration for Transaction model."""

        db_table = "transaction"
        verbose_name = _("Transaction")
        verbose_name_plural = _("Transactions")
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["dataset"]),
            models.Index(fields=["timestamp"]),
            models.Index(fields=["source_city"]),
            models.Index(fields=["destination_city"]),
            models.Index(fields=["is_anomaly"]),
            models.Index(fields=["dataset", "timestamp"]),
            models.Index(fields=["source_city", "destination_city"]),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(packet_count__gt=0),
                name="positive_packet_count",
            ),
            models.CheckConstraint(
                check=models.Q(bandwidth__gte=0),
                name="positive_bandwidth",
            ),
            models.CheckConstraint(
                check=models.Q(latency__gte=0),
                name="positive_latency",
            ),
        ]

    def __str__(self) -> str:
        """String representation of Transaction."""
        return f"{self.source_city.city_name} → {self.destination_city.city_name} ({self.protocol})"

    def get_absolute_url(self) -> str:
        """Get absolute URL for transaction detail view."""
        from django.urls import reverse

        return reverse("graph_engine:transaction_detail", kwargs={"pk": self.pk})
