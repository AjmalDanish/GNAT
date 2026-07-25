"""
API Views for Graph Engine.

This module provides REST API views for graph engine models.

Architecture:
- Django REST Framework ViewSets
- Clean Architecture: Presentation Layer
- Pagination, filtering, and permissions

Status: Phase 2 - Issue #1
"""
import hashlib
import logging
from datetime import datetime

from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import City, Country, Dataset, Transaction
from .repositories import CityRepository, CountryRepository, DatasetRepository, TransactionRepository
from .serializers import (
    CountrySerializer,
    CitySerializer,
    CityListSerializer,
    DatasetSerializer,
    DatasetCreateSerializer,
    DatasetStatisticsSerializer,
    TransactionSerializer,
    TransactionListSerializer,
    GenerateDatasetSerializer,
)
from .services.city_loader import CityDataLoader
from .services.traffic_generator import SyntheticTrafficGenerator

logger = logging.getLogger(__name__)

# Repository instances
country_repo = CountryRepository()
city_repo = CityRepository()
dataset_repo = DatasetRepository()
transaction_repo = TransactionRepository()


class CountryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Country model."""

    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["continent", "iso_code"]
    search_fields = ["country_name", "iso_code", "iso_code_3"]
    ordering_fields = ["country_name", "continent"]
    ordering = ["country_name"]


class CityViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for City model."""

    queryset = City.objects.select_related("country").all()
    permission_classes = [IsAuthenticated]
    filterset_fields = ["country", "country__continent"]
    search_fields = ["city_name", "country__country_name"]
    ordering_fields = ["city_name", "population"]
    ordering = ["city_name"]

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "list":
            return CityListSerializer
        return CitySerializer

    @action(detail=False, methods=["get"])
    def hubs(self, request):
        """Get top hub cities by population."""
        n = int(request.query_params.get("n", 10))
        hubs = city_repo.get_hubs(n)
        serializer = CityListSerializer(hubs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def random(self, request):
        """Get random cities."""
        n = int(request.query_params.get("n", 10))
        cities = city_repo.get_random(n)
        serializer = CityListSerializer(cities, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def search(self, request):
        """Search cities by name."""
        query = request.query_params.get("q", "")
        cities = city_repo.search(query)
        serializer = CityListSerializer(cities, many=True)
        return Response(serializer.data)


class DatasetViewSet(viewsets.ModelViewSet):
    """ViewSet for Dataset model."""

    permission_classes = [IsAuthenticated]
    filterset_fields = ["status", "source", "version"]
    search_fields = ["dataset_name", "description"]
    ordering_fields = ["created_at", "dataset_name", "status"]
    ordering = ["-created_at"]

    def get_queryset(self):
        """Get filtered queryset."""
        queryset = Dataset.objects.select_related("created_by")
        
        # Filter by user if not admin
        if not self.request.user.is_staff:
            queryset = queryset.filter(created_by=self.request.user)
        
        return queryset

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "create":
            return DatasetCreateSerializer
        return DatasetSerializer

    def perform_create(self, serializer):
        """Create dataset with current user."""
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=["get"])
    def statistics(self, request, pk=None):
        """Get dataset statistics."""
        dataset = self.get_object()
        stats = transaction_repo.get_statistics(str(dataset.id))
        serializer = DatasetStatisticsSerializer(stats)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def transactions(self, request, pk=None):
        """Get transactions for this dataset."""
        dataset = self.get_object()
        transactions = transaction_repo.get_by_dataset(str(dataset.id))
        
        # Pagination
        page = self.paginate_queryset(transactions)
        if page is not None:
            serializer = TransactionListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = TransactionListSerializer(transactions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def anomalies(self, request, pk=None):
        """Get anomaly transactions for this dataset."""
        dataset = self.get_object()
        anomalies = transaction_repo.get_anomalies(str(dataset.id))
        
        page = self.paginate_queryset(anomalies)
        if page is not None:
            serializer = TransactionListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = TransactionListSerializer(anomalies, many=True)
        return Response(serializer.data)


class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Transaction model."""

    queryset = Transaction.objects.select_related(
        "source_city", "destination_city", "source_city__country", "destination_city__country"
    ).all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["protocol", "is_anomaly", "risk_label", "connection_type"]
    search_fields = [
        "source_city__city_name",
        "destination_city__city_name",
        "dataset__dataset_name",
    ]
    ordering_fields = ["timestamp", "bandwidth", "latency"]
    ordering = ["-timestamp"]

    def get_queryset(self):
        """Get filtered queryset."""
        queryset = super().get_queryset()
        dataset_id = self.request.query_params.get("dataset")
        if dataset_id:
            queryset = queryset.filter(dataset_id=dataset_id)
        return queryset

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "list":
            return TransactionListSerializer
        return TransactionSerializer


class DatasetGenerationViewSet(viewsets.ViewSet):
    """ViewSet for dataset generation operations."""

    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["post"])
    def generate(self, request):
        """
        Generate synthetic dataset.

        Request body:
        {
            "dataset_name": "My Dataset",
            "version": "1.0.0",
            "description": "Description",
            "num_transactions": 10000,
            "time_window_hours": 24,
            "pattern": "random",
            "anomaly_percentage": 0.05,
            "random_seed": 42
        }
        """
        serializer = GenerateDatasetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        
        # Build city queryset
        cities_queryset = City.objects.select_related("country").all()
        
        # Apply filters if provided
        if data.get("min_population"):
            cities_queryset = cities_queryset.filter(population__gte=data["min_population"])
        
        if data.get("continents"):
            cities_queryset = cities_queryset.filter(country__continent__in=data["continents"])

        if not cities_queryset.exists():
            return Response(
                {"error": "No cities match the specified criteria"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create dataset record
        dataset = dataset_repo.create(
            dataset_name=data["dataset_name"],
            version=data["version"],
            description=data.get("description", ""),
            configuration={
                "num_transactions": data["num_transactions"],
                "time_window_hours": data["time_window_hours"],
                "pattern": data["pattern"],
                "anomaly_percentage": data["anomaly_percentage"],
                "min_population": data.get("min_population"),
                "continents": data.get("continents"),
            },
            random_seed=data.get("random_seed"),
            created_by=request.user,
        )

        # Update status to generating
        dataset_repo.update_status(dataset, Dataset.DatasetStatus.GENERATING)

        try:
            # Generate traffic
            generator = SyntheticTrafficGenerator(
                random_seed=data.get("random_seed"),
                pattern=data["pattern"],
                anomaly_percentage=data["anomaly_percentage"],
            )

            transactions_df = generator.generate(
                cities_queryset=cities_queryset,
                num_transactions=data["num_transactions"],
                time_window_hours=data["time_window_hours"],
            )

            # Prepare transactions for database
            transactions_data = []
            for _, row in transactions_df.iterrows():
                transactions_data.append({
                    "dataset_id": dataset.id,
                    "source_city_id": row["source_city_id"],
                    "destination_city_id": row["destination_city_id"],
                    "protocol": row["protocol"],
                    "packet_count": int(row["packet_count"]),
                    "packet_size": int(row["packet_size"]),
                    "bandwidth": float(row["bandwidth"]),
                    "latency": float(row["latency"]),
                    "duration": float(row["duration"]),
                    "timestamp": row["timestamp"],
                    "is_anomaly": bool(row["is_anomaly"]),
                    "connection_type": row["connection_type"],
                    "encryption": bool(row["encryption"]),
                    "risk_label": row["risk_label"],
                })

            # Batch create transactions
            transaction_repo.create_batch(transactions_data)

            # Calculate and store statistics
            statistics = transaction_repo.get_statistics(str(dataset.id))
            dataset_repo.update_statistics(dataset, statistics)

            # Calculate checksum
            dataset.checksum = hashlib.sha256(
                f"{dataset.id}{len(transactions_data)}{statistics}".encode()
            ).hexdigest()

            # Update status to completed
            dataset_repo.update_status(dataset, Dataset.DatasetStatus.COMPLETED, len(transactions_data))

            logger.info(f"Dataset {dataset.id} generation completed")

            return Response(
                {
                    "dataset_id": str(dataset.id),
                    "dataset_name": dataset.dataset_name,
                    "version": dataset.version,
                    "record_count": dataset.record_count,
                    "statistics": statistics,
                    "message": "Dataset generated successfully",
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            logger.error(f"Dataset generation failed: {e}")
            dataset_repo.update_status(dataset, Dataset.DatasetStatus.FAILED)
            return Response(
                {"error": str(e), "dataset_id": str(dataset.id)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )