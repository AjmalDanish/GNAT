"""
Models for Graph Engine Application.

This module defines the core domain models for the synthetic data generator.

Architecture:
- Clean Architecture: Domain Layer
- Django ORM with UUID primary keys
- Geographic coordinate validation
- Enum-based field choices

Status: Phase 2 - Issue #1
"""

import uuid
from datetime import datetime

from django.db import models
from django.utils.translation import gettext_lazy as _


class Country(models.Model):
    """Country model representing countries worldwide.

    This model stores geographic and administrative information about countries.
    Cities are associated with countries via foreign key relationships.

    Attributes:
        id: UUID primary key
        iso_code: 2-letter ISO 3166-1 alpha-2 code (e.g., US, GB)
        iso_code_3: 3-letter ISO 3166-1 alpha-3 code (e.g., USA, GBR)
        country_name: Full country name
        continent: Geographic continent
        latitude: Latitude coordinate (-90 to 90)
        longitude: Longitude coordinate (-180 to 180)
    """

    class Continent(models.TextChoices):
        """Continent choices using 2-letter codes."""

        AFRICA = "AF"
        ASIA = "AS"
        EUROPE = "EU"
        NORTH_AMERICA = "NA"
        SOUTH_AMERICA = "SA"
        OCEANIA = "OC"
        ANTARCTICA = "AN"

    id: uuid.UUID = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    iso_code: str = models.CharField(max_length=2, unique=True, db_index=True)
    iso_code_3: str = models.CharField(
        max_length=3, unique=True, db_index=True, null=True, blank=True
    )
    country_name: str = models.CharField(max_length=100, unique=True, db_index=True)
    continent: str = models.CharField(
        max_length=2, choices=Continent.choices, db_index=True
    )
    latitude: float = models.FloatField(null=True, blank=True)
    longitude: float = models.FloatField(null=True, blank=True)
    created_at: datetime = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at: datetime = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "country"
        verbose_name = _("country")
        verbose_name_plural = _("countries")
        indexes = [
            models.Index(fields=["country_name"], name="idx_country_name"),
            models.Index(fields=["iso_code"], name="idx_country_iso_code"),
            models.Index(fields=["continent"], name="idx_country_continent"),
            models.Index(
                fields=["iso_code", "country_name"], name="idx_country_iso_name"
            ),
        ]
        ordering = ["country_name"]

    def __str__(self) -> str:
        """String representation of Country."""
        return f"{self.country_name} ({self.iso_code})"

    def get_absolute_url(self) -> str:
        """Get absolute URL for country detail view."""
        from django.urls import reverse

        return reverse("graph_engine:country_detail", kwargs={"pk": self.pk})


class City(models.Model):
    """City model representing cities worldwide.

    This model stores geographic and demographic information about cities.
    Cities are associated with countries via foreign key relationships.

    Attributes:
        id: UUID primary key
        country: Foreign key to Country
        city_name: City name
        latitude: Latitude coordinate (-90 to 90)
        longitude: Longitude coordinate (-180 to 180)
        population: City population
        timezone: IANA timezone identifier
    """

    id: uuid.UUID = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    country: Country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        related_name="cities",
        db_index=True,
    )
    city_name: str = models.CharField(max_length=100, db_index=True)
    latitude: float = models.FloatField(db_index=True)
    longitude: float = models.FloatField(db_index=True)
    population: int = models.IntegerField(null=True, blank=True)
    timezone: str = models.CharField(max_length=50, null=True, blank=True)
    created_at: datetime = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at: datetime = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "city"
        verbose_name = _("city")
        verbose_name_plural = _("cities")
        constraints = [
            models.CheckConstraint(
                check=models.Q(latitude__gte=-90, latitude__lte=90),
                name="valid_latitude",
            ),
            models.CheckConstraint(
                check=models.Q(longitude__gte=-180, longitude__lte=180),
                name="valid_longitude",
            ),
            models.CheckConstraint(
                check=models.Q(population__gte=0), name="positive_population"
            ),
        ]
        indexes = [
            models.Index(fields=["country"], name="idx_city_country"),
            models.Index(fields=["city_name"], name="idx_city_name"),
            models.Index(fields=["latitude", "longitude"], name="idx_city_coordinates"),
            models.Index(fields=["country", "city_name"], name="idx_city_country_name"),
        ]
        ordering = ["city_name"]

    def __str__(self) -> str:
        """String representation of City."""
        return f"{self.city_name}, {self.country.country_name}"

    @property
    def coordinates(self) -> tuple[float, float]:
        """Return coordinates as a tuple."""
        return (self.latitude, self.longitude)


class Dataset(models.Model):
    """Dataset model for synthetic data metadata tracking.

    This model stores metadata about generated synthetic datasets including
    configuration, statistics, and status information.

    Attributes:
        id: UUID primary key
        dataset_name: Human-readable dataset name
        version: Semantic version
        description: Dataset description
        source: Data source (synthetic, real, hybrid)
        status: Dataset status
        record_count: Number of records
        configuration: Generation configuration (JSON)
        random_seed: Random seed used for generation
        statistics: Dataset statistics (JSON)
        checksum: Data checksum for integrity
    """

    class DatasetStatus(models.TextChoices):
        """Dataset lifecycle status."""

        PENDING = "PENDING"
        GENERATING = "GENERATING"
        COMPLETED = "COMPLETED"
        FAILED = "FAILED"
        ARCHIVED = "ARCHIVED"

    class DataSource(models.TextChoices):
        """Data source type."""

        SYNTHETIC = "synthetic"
        REAL = "real"
        HYBRID = "hybrid"

    id: uuid.UUID = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    dataset_name: str = models.CharField(max_length=255, db_index=True)
    description: models.TextField = models.TextField(blank=True)
    source: str = models.CharField(
        max_length=20, choices=DataSource.choices, default=DataSource.SYNTHETIC
    )
    version: str = models.CharField(max_length=20, db_index=True)
    created_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="datasets",
    )
    created_at: datetime = models.DateTimeField(auto_now_add=True, db_index=True)
    status: str = models.CharField(
        max_length=20, choices=DatasetStatus.choices, default=DatasetStatus.PENDING
    )
    record_count: int = models.IntegerField(default=0, db_index=True)
    configuration: models.JSONField(default=dict, blank=True)
    random_seed: int = models.IntegerField(null=True, blank=True)
    statistics: models.JSONField(default=dict, blank=True)
    checksum: models.CharField(max_length=64, blank=True)

    class Meta:
        db_table = "dataset"
        verbose_name = _("dataset")
        verbose_name_plural = _("datasets")
        constraints = [
            models.CheckConstraint(
                check=models.Q(record_count__gte=0), name="non_negative_record_count"
            ),
            models.CheckConstraint(
                check=models.Q(version__regex=r"^\d+\.\d+\.\d+$"),
                name="valid_version_format",
            ),
        ]
        indexes = [
            models.Index(fields=["version"], name="idx_dataset_version"),
            models.Index(fields=["status"], name="idx_dataset_status"),
            models.Index(fields=["created_at"], name="idx_dataset_created_at"),
            models.Index(
                fields=["status", "created_at"], name="idx_dataset_status_created"
            ),
        ]
        unique_together = [["dataset_name", "version"]]
        ordering = ["-created_at"]

    def __str__(self) -> str:
        """String representation of Dataset."""
        return f"{self.dataset_name} v{self.version}"

    def mark_generating(self) -> None:
        """Mark dataset as generating."""
        self.status = self.DatasetStatus.GENERATING
        self.save(update_fields=["status"])

    def mark_completed(self, record_count: int) -> None:
        """Mark dataset as completed."""
        self.status = self.DatasetStatus.COMPLETED
        self.record_count = record_count
        self.save(update_fields=["status", "record_count"])

    def mark_failed(self) -> None:
        """Mark dataset as failed."""
        self.status = self.DatasetStatus.FAILED
        self.save(update_fields=["status"])


class Transaction(models.Model):
    """Transaction model for individual network traffic records.

    This model stores individual network traffic transactions between cities
    including protocol information, metrics, and anomaly classification.

    Attributes:
        id: UUID primary key
        dataset: Foreign key to Dataset
        source_city: Origin city
        destination_city: Destination city
        protocol: Network protocol
        packet_count: Number of packets
        packet_size: Packet size in bytes
        bandwidth: Bandwidth in Mbps
        latency: Latency in milliseconds
        duration: Connection duration in seconds
        timestamp: Transaction timestamp
        is_anomaly: Anomaly flag
        connection_type: Connection type
        encryption: Encryption flag
        risk_label: Risk classification
    """

    class Protocol(models.TextChoices):
        """Network protocol types."""

        HTTP = "HTTP"
        HTTPS = "HTTPS"
        SSH = "SSH"
        FTP = "FTP"
        SMTP = "SMTP"
        DNS = "DNS"
        TCP = "TCP"
        UDP = "UDP"
        ICMP = "ICMP"

    class ConnectionType(models.TextChoices):
        """Connection type classification."""

        CLIENT_SERVER = "CLIENT_SERVER"
        PEER_TO_PEER = "PEER_TO_PEER"
        SERVER_TO_SERVER = "SERVER_TO_SERVER"
        IOT = "IOT"
        CDN = "CDN"

    class RiskLabel(models.TextChoices):
        """Risk classification labels."""

        NORMAL = "NORMAL"
        LOW = "LOW"
        MEDIUM = "MEDIUM"
        HIGH = "HIGH"
        CRITICAL = "CRITICAL"

    id: uuid.UUID = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    dataset: Dataset = models.ForeignKey(
        Dataset, on_delete=models.CASCADE, related_name="transactions", db_index=True
    )
    source_city: City = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        related_name="outgoing_transactions",
        db_index=True,
    )
    destination_city: City = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        related_name="incoming_transactions",
        db_index=True,
    )
    packet_count: int = models.IntegerField()
    packet_size: int = models.IntegerField(default=1500, db_index=True)
    bandwidth: float = models.FloatField(db_index=True)
    latency: float = models.FloatField(db_index=True)
    duration: float = models.FloatField(default=0.0)
    protocol: str = models.CharField(
        max_length=10, choices=Protocol.choices, default=Protocol.HTTPS, db_index=True
    )
    timestamp: datetime = models.DateTimeField(db_index=True)
    is_anomaly: bool = models.BooleanField(default=False, db_index=True)
    connection_type: str = models.CharField(
        max_length=20,
        choices=ConnectionType.choices,
        default=ConnectionType.CLIENT_SERVER,
    )
    encryption: bool = models.BooleanField(default=False)
    risk_label: str = models.CharField(
        max_length=10, choices=RiskLabel.choices, default=RiskLabel.NORMAL
    )

    class Meta:
        db_table = "transaction"
        verbose_name = _("transaction")
        verbose_name_plural = _("transactions")
        constraints = [
            models.CheckConstraint(
                check=models.Q(packet_count__gt=0), name="positive_packet_count"
            ),
            models.CheckConstraint(
                check=models.Q(bandwidth__gte=0), name="non_negative_bandwidth"
            ),
            models.CheckConstraint(
                check=models.Q(latency__gte=0), name="non_negative_latency"
            ),
            models.CheckConstraint(
                check=~models.Q(source_city=models.F("id")),
                name="source_not_destination",
            ),
        ]
        indexes = [
            models.Index(fields=["dataset"], name="idx_transaction_dataset"),
            models.Index(fields=["timestamp"], name="idx_transaction_timestamp"),
            models.Index(fields=["source_city"], name="idx_transaction_source"),
            models.Index(
                fields=["destination_city"], name="idx_transaction_destination"
            ),
            models.Index(fields=["is_anomaly"], name="idx_transaction_is_anomaly"),
            models.Index(fields=["dataset", "timestamp"], name="idx_trx_dst_ts"),
            models.Index(
                fields=["source_city", "destination_city"],
                name="idx_transaction_source_dest",
            ),
        ]
        ordering = ["-timestamp"]

    def __str__(self) -> str:
        """String representation of Transaction."""
        return (
            f"{self.source_city.city_name} -> {self.destination_city.city_name} "
            f"({self.protocol}) - {'⚠️' if self.is_anomaly else '✓'}"
        )
