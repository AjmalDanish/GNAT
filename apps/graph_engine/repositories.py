"""
Repositories for Graph Engine.

This module provides data access layer for graph engine models.

Architecture:
- Clean Architecture: Repository Pattern
- Separates data access from business logic
- Query optimization with select_related/prefetch_related

Status: Phase 2 - Issue #1
"""
import logging
from typing import Optional

from django.db import models
from django.db.models import Q, Count

from .models import City, Country, Dataset, Transaction

logger = logging.getLogger(__name__)


class CountryRepository:
    """Repository for Country model queries."""

    def get_by_iso_code(self, iso_code: str) -> Optional[Country]:
        """
        Get country by ISO code.

        Args:
            iso_code: ISO 3166-1 alpha-2 code.

        Returns:
            Country object or None.
        """
        try:
            return Country.objects.get(iso_code__iexact=iso_code)
        except Country.DoesNotExist:
            return None

    def get_by_name(self, name: str) -> Optional[Country]:
        """
        Get country by name.

        Args:
            name: Country name.

        Returns:
            Country object or None.
        """
        try:
            return Country.objects.get(country_name__iexact=name)
        except Country.DoesNotExist:
            return None

    def get_all(self) -> models.QuerySet:
        """
        Get all countries.

        Returns:
            QuerySet of all countries.
        """
        return Country.objects.all()

    def get_by_continent(self, continent: str) -> models.QuerySet:
        """
        Get countries by continent.

        Args:
            continent: Continent code.

        Returns:
            QuerySet of countries in the continent.
        """
        return Country.objects.filter(continent=continent)

    def create(
        self,
        iso_code: str,
        country_name: str,
        continent: str,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        iso_code_3: Optional[str] = None,
    ) -> Country:
        """
        Create a new country.

        Args:
            iso_code: ISO 3166-1 alpha-2 code.
            country_name: Full country name.
            continent: Continent code.
            latitude: Approximate center latitude.
            longitude: Approximate center longitude.
            iso_code_3: ISO 3166-1 alpha-3 code.

        Returns:
            Created Country object.
        """
        country = Country.objects.create(
            iso_code=iso_code,
            country_name=country_name,
            continent=continent,
            latitude=latitude,
            longitude=longitude,
            iso_code_3=iso_code_3,
        )
        logger.info(f"Created country: {country}")
        return country

    def create_batch(self, countries_data: list[dict]) -> int:
        """
        Create multiple countries in batch.

        Args:
            countries_data: List of country data dictionaries.

        Returns:
            Number of countries created.
        """
        countries = [Country(**data) for data in countries_data]
        Country.objects.bulk_create(countries, ignore_conflicts=True)
        logger.info(f"Created {len(countries)} countries in batch")
        return len(countries)


class CityRepository:
    """Repository for City model queries."""

    def get_by_id(self, city_id: str) -> Optional[City]:
        """
        Get city by UUID.

        Args:
            city_id: City UUID.

        Returns:
            City object or None.
        """
        try:
            return City.objects.select_related("country").get(id=city_id)
        except City.DoesNotExist:
            return None

    def get_by_name(self, name: str) -> Optional[City]:
        """
        Get city by name.

        Args:
            name: City name.

        Returns:
            City object or None.
        """
        try:
            return City.objects.select_related("country").get(city_name__iexact=name)
        except City.DoesNotExist:
            return None

    def get_all(self) -> models.QuerySet:
        """
        Get all cities with country preloaded.

        Returns:
            QuerySet of all cities.
        """
        return City.objects.select_related("country").all()

    def get_by_country(self, country_id: str) -> models.QuerySet:
        """
        Get cities by country.

        Args:
            country_id: Country UUID or ISO code.

        Returns:
            QuerySet of cities in the country.
        """
        return City.objects.filter(country_id=country_id).select_related("country")

    def get_by_continent(self, continent: str) -> models.QuerySet:
        """
        Get cities by continent.

        Args:
            continent: Continent code.

        Returns:
            QuerySet of cities in the continent.
        """
        return City.objects.filter(country__continent=continent).select_related("country")

    def search(self, query: str) -> models.QuerySet:
        """
        Search cities by name.

        Args:
            query: Search query.

        Returns:
            QuerySet of matching cities.
        """
        return City.objects.filter(
            Q(city_name__icontains=query) | Q(country__country_name__icontains=query)
        ).select_related("country")

    def get_random(self, n: int = 1) -> list[City]:
        """
        Get n random cities.

        Args:
            n: Number of cities to return.

        Returns:
            List of City objects.
        """
        return list(City.objects.order_by("?")[:n])

    def get_hubs(self, n: int = 10) -> models.QuerySet:
        """
        Get top n cities by population (hubs).

        Args:
            n: Number of hub cities.

        Returns:
            QuerySet of hub cities.
        """
        return City.objects.filter(
            population__isnull=False
        ).order_by("-population")[:n].select_related("country")

    def get_nearby(
        self, latitude: float, longitude: float, radius_km: float = 100
    ) -> models.QuerySet:
        """
        Get cities within a radius.

        Args:
            latitude: Center latitude.
            longitude: Center longitude.
            radius_km: Radius in kilometers.

        Returns:
            QuerySet of nearby cities.
        """
        # Simple bounding box approximation
        # 1 degree ≈ 111 km
        lat_delta = radius_km / 111.0
        lon_delta = radius_km / (111.0 * abs(latitude) if latitude != 0 else 111.0)

        return City.objects.filter(
            latitude__range=(latitude - lat_delta, latitude + lat_delta),
            longitude__range=(longitude - lon_delta, longitude + lon_delta),
        ).select_related("country")

    def create(
        self,
        country: Country,
        city_name: str,
        latitude: float,
        longitude: float,
        population: Optional[int] = None,
        timezone: Optional[str] = None,
    ) -> City:
        """
        Create a new city.

        Args:
            country: Country object.
            city_name: City name.
            latitude: Geographic latitude.
            longitude: Geographic longitude.
            population: City population.
            timezone: Timezone identifier.

        Returns:
            Created City object.
        """
        city = City.objects.create(
            country=country,
            city_name=city_name,
            latitude=latitude,
            longitude=longitude,
            population=population,
            timezone=timezone,
        )
        logger.info(f"Created city: {city}")
        return city

    def create_batch(self, cities_data: list[dict]) -> int:
        """
        Create multiple cities in batch.

        Args:
            cities_data: List of city data dictionaries.

        Returns:
            Number of cities created.
        """
        cities = [City(**data) for data in cities_data]
        City.objects.bulk_create(cities, ignore_conflicts=True)
        logger.info(f"Created {len(cities)} cities in batch")
        return len(cities)


class DatasetRepository:
    """Repository for Dataset model queries."""

    def get_by_id(self, dataset_id: str) -> Optional[Dataset]:
        """
        Get dataset by UUID.

        Args:
            dataset_id: Dataset UUID.

        Returns:
            Dataset object or None.
        """
        try:
            return Dataset.objects.select_related("created_by").get(id=dataset_id)
        except Dataset.DoesNotExist:
            return None

    def get_all(self) -> models.QuerySet:
        """
        Get all datasets.

        Returns:
            QuerySet of all datasets.
        """
        return Dataset.objects.select_related("created_by").all()

    def get_by_status(self, status: str) -> models.QuerySet:
        """
        Get datasets by status.

        Args:
            status: Dataset status.

        Returns:
            QuerySet of datasets with the status.
        """
        return Dataset.objects.filter(status=status).select_related("created_by")

    def get_by_user(self, user_id: str) -> models.QuerySet:
        """
        Get datasets created by a user.

        Args:
            user_id: User UUID.

        Returns:
            QuerySet of datasets created by the user.
        """
        return Dataset.objects.filter(created_by_id=user_id).select_related("created_by")

    def create(
        self,
        dataset_name: str,
        version: str,
        description: str = "",
        source: str = "synthetic",
        configuration: Optional[dict] = None,
        random_seed: Optional[int] = None,
        created_by=None,
    ) -> Dataset:
        """
        Create a new dataset.

        Args:
            dataset_name: Dataset name.
            version: Dataset version.
            description: Dataset description.
            source: Data source.
            configuration: Generation configuration.
            random_seed: Random seed used.
            created_by: User who created the dataset.

        Returns:
            Created Dataset object.
        """
        dataset = Dataset.objects.create(
            dataset_name=dataset_name,
            version=version,
            description=description,
            source=source,
            configuration=configuration or {},
            random_seed=random_seed,
            created_by=created_by,
            status=Dataset.DatasetStatus.PENDING,
        )
        logger.info(f"Created dataset: {dataset}")
        return dataset

    def update_status(
        self, dataset: Dataset, status: str, record_count: int = None
    ) -> None:
        """
        Update dataset status.

        Args:
            dataset: Dataset object.
            status: New status.
            record_count: Number of records (if completed).
        """
        dataset.status = status
        if record_count is not None:
            dataset.record_count = record_count
        dataset.save(update_fields=["status", "record_count"])
        logger.info(f"Updated dataset {dataset.id} status to {status}")

    def update_statistics(self, dataset: Dataset, statistics: dict) -> None:
        """
        Update dataset statistics.

        Args:
            dataset: Dataset object.
            statistics: Statistics dictionary.
        """
        dataset.statistics = statistics
        dataset.save(update_fields=["statistics"])
        logger.info(f"Updated statistics for dataset {dataset.id}")


class TransactionRepository:
    """Repository for Transaction model queries."""

    def get_by_id(self, transaction_id: str) -> Optional[Transaction]:
        """
        Get transaction by UUID.

        Args:
            transaction_id: Transaction UUID.

        Returns:
            Transaction object or None.
        """
        try:
            return (
                Transaction.objects.select_related(
                    "dataset", "source_city", "destination_city"
                )
                .get(id=transaction_id)
            )
        except Transaction.DoesNotExist:
            return None

    def get_by_dataset(self, dataset_id: str) -> models.QuerySet:
        """
        Get transactions by dataset.

        Args:
            dataset_id: Dataset UUID.

        Returns:
            QuerySet of transactions in the dataset.
        """
        return (
            Transaction.objects.filter(dataset_id=dataset_id)
            .select_related("source_city", "destination_city")
            .order_by("timestamp")
        )

    def get_anomalies(self, dataset_id: str) -> models.QuerySet:
        """
        Get anomaly transactions.

        Args:
            dataset_id: Dataset UUID.

        Returns:
            QuerySet of anomaly transactions.
        """
        return (
            Transaction.objects.filter(dataset_id=dataset_id, is_anomaly=True)
            .select_related("source_city", "destination_city")
            .order_by("timestamp")
        )

    def get_by_city_pair(
        self, source_city_id: str, destination_city_id: str
    ) -> models.QuerySet:
        """
        Get transactions between a city pair.

        Args:
            source_city_id: Source city UUID.
            destination_city_id: Destination city UUID.

        Returns:
            QuerySet of transactions between the cities.
        """
        return (
            Transaction.objects.filter(
                source_city_id=source_city_id, destination_city_id=destination_city_id
            )
            .select_related("source_city", "destination_city")
            .order_by("timestamp")
        )

    def get_by_protocol(self, dataset_id: str, protocol: str) -> models.QuerySet:
        """
        Get transactions by protocol.

        Args:
            dataset_id: Dataset UUID.
            protocol: Protocol name.

        Returns:
            QuerySet of transactions with the protocol.
        """
        return (
            Transaction.objects.filter(dataset_id=dataset_id, protocol=protocol)
            .select_related("source_city", "destination_city")
            .order_by("timestamp")
        )

    def create_batch(self, transactions_data: list[dict]) -> int:
        """
        Create multiple transactions in batch.

        Args:
            transactions_data: List of transaction data dictionaries.

        Returns:
            Number of transactions created.
        """
        transactions = [Transaction(**data) for data in transactions_data]
        Transaction.objects.bulk_create(transactions, batch_size=1000)
        logger.info(f"Created {len(transactions)} transactions in batch")
        return len(transactions)

    def get_statistics(self, dataset_id: str) -> dict:
        """
        Get transaction statistics for a dataset.

        Args:
            dataset_id: Dataset UUID.

        Returns:
            Dictionary of statistics.
        """
        qs = Transaction.objects.filter(dataset_id=dataset_id)

        total = qs.count()
        anomalies = qs.filter(is_anomaly=True).count()
        total_bandwidth = qs.aggregate(total=models.Sum("bandwidth"))["total"] or 0
        avg_latency = qs.aggregate(avg=models.Avg("latency"))["avg"] or 0

        return {
            "total_transactions": total,
            "anomaly_count": anomalies,
            "anomaly_percentage": (anomalies / total * 100) if total > 0 else 0,
            "total_bandwidth": float(total_bandwidth),
            "average_latency": float(avg_latency),
        }