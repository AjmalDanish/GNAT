"""
Graph Repository.

This module provides data access operations for graph metadata.

Architecture:
- Clean Architecture: Infrastructure Layer
- Repository Pattern
- Database operations for graph persistence

Status: Phase 2 - Graph Construction Engine
"""

import uuid
from typing import Any

from django.core.exceptions import ObjectDoesNotExist

from ..models import Dataset


class GraphRepository:
    """Repository for graph metadata operations."""

    @staticmethod
    def get_dataset(dataset_id: uuid.UUID) -> Dataset | None:
        """Retrieve a dataset by ID.

        Args:
            dataset_id: Dataset UUID

        Returns:
            Dataset instance or None
        """
        try:
            return Dataset.objects.get(id=dataset_id)
        except ObjectDoesNotExist:
            return None

    @staticmethod
    def get_dataset_by_name(name: str) -> Dataset | None:
        """Retrieve a dataset by name.

        Args:
            name: Dataset name

        Returns:
            Dataset instance or None
        """
        try:
            return Dataset.objects.get(dataset_name=name)
        except ObjectDoesNotExist:
            return None

    @staticmethod
    def list_datasets(status: str | None = None, version: str | None = None) -> list[Dataset]:
        """List datasets with optional filters.

        Args:
            status: Filter by status
            version: Filter by version

        Returns:
            List of Dataset instances
        """
        queryset = Dataset.objects.all()

        if status:
            queryset = queryset.filter(status=status)
        if version:
            queryset = queryset.filter(version=version)

        return list(queryset)

    @staticmethod
    def save_graph_metadata(
        dataset_id: uuid.UUID,
        graph_data: dict[str, Any],
        metadata: dict[str, Any] | None = None,
    ) -> Dataset:
        """Save graph metadata to a dataset.

        Args:
            dataset_id: Dataset ID
            graph_data: Graph serialization data
            metadata: Additional metadata

        Returns:
            Updated Dataset instance
        """
        dataset = GraphRepository.get_dataset(dataset_id)

        if dataset is None:
            raise ValueError(f"Dataset {dataset_id} not found")

        # Store graph data in configuration JSON field
        config = dataset.configuration or {}
        config["graph"] = graph_data

        if metadata:
            config["graph_metadata"] = metadata

        dataset.configuration = config
        dataset.save()

        return dataset

    @staticmethod
    def load_graph_metadata(dataset_id: uuid.UUID) -> dict[str, Any] | None:
        """Load graph metadata from a dataset.

        Args:
            dataset_id: Dataset ID

        Returns:
            Graph data dict or None
        """
        dataset = GraphRepository.get_dataset(dataset_id)

        if dataset is None:
            return None

        config = dataset.configuration or {}
        return config.get("graph")

    @staticmethod
    def get_dataset_statistics(dataset_id: uuid.UUID) -> dict[str, Any]:
        """Get statistics for a dataset.

        Args:
            dataset_id: Dataset ID

        Returns:
            Dict with dataset statistics
        """
        from ..models import Transaction

        dataset = GraphRepository.get_dataset(dataset_id)

        if dataset is None:
            return {}

        transaction_count = Transaction.objects.filter(dataset_id=dataset_id).count()

        return {
            "dataset_id": str(dataset_id),
            "dataset_name": dataset.dataset_name,
            "version": dataset.version,
            "status": dataset.status,
            "record_count": dataset.record_count,
            "transaction_count": transaction_count,
            "created_at": dataset.created_at.isoformat(),
        }

    @staticmethod
    def get_transaction_count_by_city(dataset_id: uuid.UUID) -> dict[str, int]:
        """Get transaction counts grouped by city.

        Args:
            dataset_id: Dataset ID

        Returns:
            Dict mapping city names to transaction counts
        """
        from django.db.models import Count

        from ..models import Transaction

        # Count transactions as source
        source_counts = (
            Transaction.objects.filter(dataset_id=dataset_id)
            .values("source_city__city_name")
            .annotate(count=Count("id"))
        )

        # Count transactions as destination
        dest_counts = (
            Transaction.objects.filter(dataset_id=dataset_id)
            .values("destination_city__city_name")
            .annotate(count=Count("id"))
        )

        # Combine counts
        counts = {}
        for item in source_counts:
            city = item["source_city__city_name"]
            counts[city] = counts.get(city, 0) + item["count"]

        for item in dest_counts:
            city = item["destination_city__city_name"]
            counts[city] = counts.get(city, 0) + item["count"]

        return counts

    @staticmethod
    def get_transaction_count_by_country(dataset_id: uuid.UUID) -> dict[str, int]:
        """Get transaction counts grouped by country.

        Args:
            dataset_id: Dataset ID

        Returns:
            Dict mapping country names to transaction counts
        """
        from django.db.models import Count

        from ..models import Transaction

        # Count transactions by source country
        source_counts = (
            Transaction.objects.filter(dataset_id=dataset_id)
            .values("source_city__country__country_name")
            .annotate(count=Count("id"))
        )

        # Count transactions by destination country
        dest_counts = (
            Transaction.objects.filter(dataset_id=dataset_id)
            .values("destination_city__country__country_name")
            .annotate(count=Count("id"))
        )

        # Combine counts
        counts = {}
        for item in source_counts:
            country = item["source_city__country__country_name"]
            counts[country] = counts.get(country, 0) + item["count"]

        for item in dest_counts:
            country = item["destination_city__country__country_name"]
            counts[country] = counts.get(country, 0) + item["count"]

        return counts

    @staticmethod
    def get_top_cities_by_traffic(dataset_id: uuid.UUID, limit: int = 10) -> list[dict[str, Any]]:
        """Get top cities by total transaction traffic.

        Args:
            dataset_id: Dataset ID
            limit: Maximum number of cities to return

        Returns:
            List of dicts with city_name and transaction_count
        """
        from django.db.models import Count, Sum

        from ..models import Transaction

        # Combine source and destination traffic
        traffic_by_city = (
            Transaction.objects.filter(dataset_id=dataset_id)
            .values("city_name")
            .annotate(
                total_count=Count("id"),
                total_bandwidth=Sum("bandwidth"),
            )
            .order_by("-total_count")[:limit]
        )

        return [
            {
                "city_name": item["city_name"],
                "transaction_count": item["total_count"],
                "total_bandwidth": float(item["total_bandwidth"] or 0),
            }
            for item in traffic_by_city
        ]
