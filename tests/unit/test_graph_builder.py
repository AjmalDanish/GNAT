"""
Unit Tests for GraphBuilder Service.

Status: Phase 2 - Graph Construction Engine
"""

import pytest

from apps.graph_engine.backends.networkx_backend import NetworkXBackend
from apps.graph_engine.services.graph_builder import GraphBuilder


@pytest.mark.django_db
class TestGraphBuilder:
    """Tests for GraphBuilder service."""

    def test_initialization_with_default_backend(self):
        """Test initialization with default NetworkX backend."""
        builder = GraphBuilder()
        assert isinstance(builder.backend, NetworkXBackend)

    def test_initialization_with_custom_backend(self):
        """Test initialization with custom backend."""
        custom_backend = NetworkXBackend()
        builder = GraphBuilder(backend=custom_backend)
        assert builder.backend is custom_backend

    def test_get_graph(self):
        """Test getting the graph instance."""
        builder = GraphBuilder()
        graph = builder.get_graph()
        assert isinstance(graph, NetworkXBackend)

    def test_reset(self):
        """Test resetting the graph."""
        builder = GraphBuilder()
        builder.backend.add_node(node_id="city1")
        builder.reset()
        assert builder.backend.get_node_count() == 0

    def test_build_from_empty_dataset(self, db):
        """Test building from a dataset with no transactions."""
        from apps.graph_engine.models import Dataset

        dataset = Dataset.objects.create(
            dataset_name="Empty Dataset",
            version="1.0.0",
        )

        builder = GraphBuilder()
        result = builder.build_from_dataset(dataset.id)

        assert result["node_count"] == 0
        assert result["edge_count"] == 0
        assert result["transaction_count"] == 0

    def test_build_from_dataset_filters_anomalies(self, db):
        """Test that build_from_dataset can filter anomalies."""
        from apps.graph_engine.models import City, Country, Dataset, Transaction

        country = Country.objects.create(
            iso_code="US",
            country_name="United States",
            continent="NA",
        )
        city1 = City.objects.create(
            country=country,
            city_name="New York",
            latitude=40.7128,
            longitude=-74.0060,
        )
        city2 = City.objects.create(
            country=country,
            city_name="Los Angeles",
            latitude=34.0522,
            longitude=-118.2437,
        )
        dataset = Dataset.objects.create(
            dataset_name="Test Dataset",
            version="1.0.0",
        )

        # Create normal transaction
        from django.utils import timezone

        Transaction.objects.create(
            dataset=dataset,
            source_city=city1,
            destination_city=city2,
            protocol="TCP",
            packet_count=100,
            bandwidth=1000.0,
            latency=100.5,
            timestamp=timezone.now(),
        )

        # Create anomalous transaction
        Transaction.objects.create(
            dataset=dataset,
            source_city=city2,
            destination_city=city1,
            protocol="TCP",
            packet_count=100,
            bandwidth=1000.0,
            latency=100.5,
            timestamp=timezone.now(),
            is_anomaly=True,
        )

        builder = GraphBuilder()

        # Without filtering anomalies
        result_with = builder.build_from_dataset(dataset.id, include_anomalies=True)
        assert result_with["transaction_count"] == 2
        assert result_with["edge_count"] == 2

        # Filter anomalies
        builder.reset()
        result_without = builder.build_from_dataset(dataset.id, include_anomalies=False)
        assert result_without["transaction_count"] == 1
        assert result_without["edge_count"] == 1

    def test_batch_processing(self, db):
        """Test that batch processing works correctly."""
        from apps.graph_engine.models import City, Country, Dataset, Transaction

        country = Country.objects.create(
            iso_code="US",
            country_name="United States",
            continent="NA",
        )
        city1 = City.objects.create(
            country=country,
            city_name="New York",
            latitude=40.7128,
            longitude=-74.0060,
        )
        city2 = City.objects.create(
            country=country,
            city_name="Los Angeles",
            latitude=34.0522,
            longitude=-118.2437,
        )
        dataset = Dataset.objects.create(
            dataset_name="Test Dataset",
            version="1.0.0",
        )

        # Create 50 transactions
        from django.utils import timezone

        for i in range(50):
            Transaction.objects.create(
                dataset=dataset,
                source_city=city1,
                destination_city=city2,
                protocol="TCP",
                packet_count=100 + i,
                bandwidth=1000.0,
                latency=100.5,
                timestamp=timezone.now(),
            )

        builder = GraphBuilder()
        result = builder.build_from_dataset(dataset.id, batch_size=10)

        assert result["transaction_count"] == 50
        assert result["node_count"] == 2
        assert result["edge_count"] == 1

    def test_node_attributes_from_city(self, db):
        """Test that node attributes are populated from city data."""
        from apps.graph_engine.models import City, Country, Dataset, Transaction

        country = Country.objects.create(
            iso_code="US",
            country_name="United States",
            continent="NA",
        )
        city = City.objects.create(
            country=country,
            city_name="New York",
            latitude=40.7128,
            longitude=-74.0060,
            timezone="America/New_York",
        )
        dataset = Dataset.objects.create(
            dataset_name="Test Dataset",
            version="1.0.0",
        )

        Transaction.objects.create(
            dataset=dataset,
            source_city=city,
            destination_city=city,
            protocol="TCP",
            packet_count=100,
            bandwidth=1000.0,
            latency=100.5,
            timestamp=timezone.now(),
        )

        builder = GraphBuilder()
        builder.build_from_dataset(dataset.id)

        node_attrs = builder.backend.get_node_attributes(str(city.id))
        assert node_attrs["country"] == "United States"
        assert node_attrs["city"] == "New York"
        assert node_attrs["coordinates"] == (40.7128, -74.0060)

    def test_edge_aggregation(self, db):
        """Test that edges are aggregated when multiple transactions exist."""
        from apps.graph_engine.models import City, Country, Dataset, Transaction

        country = Country.objects.create(
            iso_code="US",
            country_name="United States",
            continent="NA",
        )
        city1 = City.objects.create(
            country=country,
            city_name="New York",
            latitude=40.7128,
            longitude=-74.0060,
        )
        city2 = City.objects.create(
            country=country,
            city_name="Los Angeles",
            latitude=34.0522,
            longitude=-118.2437,
        )
        dataset = Dataset.objects.create(
            dataset_name="Test Dataset",
            version="1.0.0",
        )

        # Create multiple transactions between same cities
        from django.utils import timezone

        Transaction.objects.create(
            dataset=dataset,
            source_city=city1,
            destination_city=city2,
            protocol="TCP",
            packet_count=100,
            bandwidth=1000.0,
            latency=100.0,
            timestamp=timezone.now(),
        )
        Transaction.objects.create(
            dataset=dataset,
            source_city=city1,
            destination_city=city2,
            protocol="TCP",
            packet_count=200,
            bandwidth=500.0,
            latency=200.0,
            timestamp=timezone.now(),
        )

        builder = GraphBuilder()
        builder.build_from_dataset(dataset.id)

        edge_attrs = builder.backend.get_edge_attributes(str(city1.id), str(city2.id))
        assert edge_attrs is not None
        assert edge_attrs["packet_count"] == 300  # Aggregated
        assert edge_attrs["bandwidth"] == 1500.0  # Sum
        # Latency is averaged
        assert edge_attrs["latency"] == 150.0
