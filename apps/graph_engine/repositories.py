"""
Repositories for Graph Engine.

This module provides data access abstraction layer following the Repository Pattern.

Architecture:
- Clean Architecture: Infrastructure Layer
- Separation of data access from business logic
- Optimized queries with select_related/prefetch_related
- Type-safe query results

Status: Phase 2 - Issue #1
"""

import uuid
from typing import Any

from django.db.models import Q

from .models import City, Country, Dataset, Transaction


class CountryRepository:
    """Repository for Country data access operations."""

    @staticmethod
    def get_by_id(country_id: uuid.UUID) -> Country | None:
        """Get country by ID."""
        return Country.objects.filter(id=country_id).first()

    @staticmethod
    def get_by_iso_code(iso_code: str) -> Country | None:
        """Get country by ISO 2-letter code."""
        return Country.objects.filter(iso_code=iso_code).first()

    @staticmethod
    def get_by_name(name: str) -> Country | None:
        """Get country by name."""
        return Country.objects.filter(country_name__icontains=name).first()

    @staticmethod
    def get_all() -> list[Country]:
        """Get all countries."""
        return list(Country.objects.all())

    @staticmethod
    def get_by_continent(continent: str) -> list[Country]:
        """Get countries by continent."""
        return list(Country.objects.filter(continent=continent))

    @staticmethod
    def search(query: str) -> list[Country]:
        """Search countries by name."""
        return list(
            Country.objects.filter(Q(country_name__icontains=query) | Q(iso_code__icontains=query))
        )


class CityRepository:
    """Repository for City data access operations."""

    @staticmethod
    def get_by_id(city_id: uuid.UUID) -> City | None:
        """Get city by ID."""
        return City.objects.select_related("country").filter(id=city_id).first()

    @staticmethod
    def get_by_country(country_id: uuid.UUID) -> list[City]:
        """Get cities by country."""
        return list(City.objects.filter(country_id=country_id).select_related("country"))

    @staticmethod
    def get_all() -> list[City]:
        """Get all cities."""
        return list(City.objects.select_related("country").all())

    @staticmethod
    def get_random(n: int = 10) -> list[City]:
        """Get N random cities."""
        return list(City.objects.select_related("country").order_by("?")[:n])

    @staticmethod
    def get_hubs(n: int = 10) -> list[City]:
        """Get top N cities by population (major hubs)."""
        return list(
            City.objects.select_related("country")
            .filter(population__isnull=False)
            .order_by("-population")[:n]
        )

    @staticmethod
    def get_nearby(city_id: uuid.UUID, n: int = 10) -> list[City]:
        """Get N nearest cities by distance."""
        city = CityRepository.get_by_id(city_id)
        if not city:
            return []

        # Simple Euclidean distance (for performance, use Haversine for production)
        all_cities = City.objects.exclude(id=city_id)
        nearby = []

        for c in all_cities:
            distance = (
                (city.latitude - c.latitude) ** 2 + (city.longitude - c.longitude) ** 2
            ) ** 0.5
            nearby.append((distance, c))

        nearby.sort(key=lambda x: x[0])
        return [city[1] for city in nearby[:n]]

    @staticmethod
    def search(query: str) -> list[City]:
        """Search cities by name."""
        return list(
            City.objects.select_related("country").filter(
                Q(city_name__icontains=query) | Q(country__country_name__icontains=query)
            )
        )


class DatasetRepository:
    """Repository for Dataset data access operations."""

    @staticmethod
    def get_by_id(dataset_id: uuid.UUID) -> Dataset | None:
        """Get dataset by ID."""
        return Dataset.objects.select_related("created_by").filter(id=dataset_id).first()

    @staticmethod
    def get_by_name_and_version(name: str, version: str) -> Dataset | None:
        """Get dataset by name and version."""
        return Dataset.objects.filter(dataset_name=name, version=version).first()

    @staticmethod
    def get_all() -> list[Dataset]:
        """Get all datasets."""
        return list(Dataset.objects.select_related("created_by").all())

    @staticmethod
    def get_by_status(status: str) -> list[Dataset]:
        """Get datasets by status."""
        return list(Dataset.objects.filter(status=status).select_related("created_by"))

    @staticmethod
    def get_recent(n: int = 10) -> list[Dataset]:
        """Get N most recent datasets."""
        return list(Dataset.objects.select_related("created_by").order_by("-created_at")[:n])

    def create(
        self,
        dataset_name: str,
        version: str,
        description: str,
        configuration: dict[str, Any],
        random_seed: int | None = None,
        created_by_id: uuid.UUID | None = None,
    ) -> Dataset:
        """Create a new dataset."""
        return Dataset.objects.create(
            dataset_name=dataset_name,
            version=version,
            description=description,
            configuration=configuration,
            random_seed=random_seed,
            created_by_id=created_by_id,
        )

    def update_status(self, dataset: Dataset, status: str) -> None:
        """Update dataset status."""
        dataset.status = status
        dataset.save(update_fields=["status"])

    def update_record_count(self, dataset: Dataset, count: int) -> None:
        """Update dataset record count."""
        dataset.record_count = count
        dataset.save(update_fields=["record_count"])

    def update_statistics(self, dataset: Dataset, statistics: dict[str, Any]) -> None:
        """Update dataset statistics."""
        dataset.statistics = statistics
        dataset.save(update_fields=["statistics"])


class TransactionRepository:
    """Repository for Transaction data access operations."""

    @staticmethod
    def get_by_id(transaction_id: uuid.UUID) -> Transaction | None:
        """Get transaction by ID."""
        return (
            Transaction.objects.select_related(
                "source_city",
                "destination_city",
                "dataset",
                "source_city__country",
                "destination_city__country",
            )
            .filter(id=transaction_id)
            .first()
        )

    @staticmethod
    def get_by_dataset(dataset_id: uuid.UUID) -> list[Transaction]:
        """Get transactions by dataset."""
        return list(
            Transaction.objects.select_related("source_city", "destination_city", "dataset").filter(
                dataset_id=dataset_id
            )
        )

    @staticmethod
    def get_anomalies(dataset_id: uuid.UUID) -> list[Transaction]:
        """Get anomaly transactions for a dataset."""
        return list(
            Transaction.objects.select_related("source_city", "destination_city", "dataset").filter(
                dataset_id=dataset_id, is_anomaly=True
            )
        )

    @staticmethod
    def get_statistics(dataset_id: uuid.UUID) -> dict[str, Any]:
        """Calculate statistics for a dataset."""
        from django.db.models import Avg, Count, Max, Min, Sum

        stats = Transaction.objects.filter(dataset_id=dataset_id).aggregate(
            total_count=Count("id"),
            anomaly_count=Count("id", filter=Q(is_anomaly=True)),
            normal_count=Count("id", filter=Q(is_anomaly=False)),
            avg_bandwidth=Avg("bandwidth"),
            avg_latency=Avg("latency"),
            max_bandwidth=Max("bandwidth"),
            max_latency=Max("latency"),
            min_bandwidth=Min("bandwidth"),
            min_latency=Min("latency"),
            total_bandwidth=Sum("bandwidth"),
        )

        # Calculate percentages
        total = stats["total_count"] or 0
        if total > 0:
            stats["anomaly_percentage"] = round((stats["anomaly_count"] or 0) / total * 100, 2)
            stats["normal_percentage"] = round((stats["normal_count"] or 0) / total * 100, 2)
        else:
            stats["anomaly_percentage"] = 0.0
            stats["normal_percentage"] = 0.0

        return stats

    def create_batch(self, transactions_data: list[dict[str, Any]], batch_size: int = 1000) -> int:
        """Create transactions in batches."""
        created = 0
        for i in range(0, len(transactions_data), batch_size):
            batch = transactions_data[i : i + batch_size]
            created += len(Transaction.objects.bulk_create([Transaction(**t) for t in batch]))
        return created
