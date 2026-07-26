"""
Additional Unit Tests for GraphBuilder Service - Coverage Extension.

Status: Phase 2 - Graph Construction Engine - Coverage >90%
"""

from django.utils import timezone

import pytest

from apps.graph_engine.backends.networkx_backend import NetworkXBackend
from apps.graph_engine.services.graph_builder import GraphBuilder


@pytest.mark.django_db
class TestGraphBuilderCoverage:
    """Additional coverage tests for GraphBuilder."""

    def test_build_from_city_pairs_with_filter(self, db):
        """Test building from city pairs with protocol filter."""
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
            dataset_name="Protocol Filter Dataset",
            version="1.0.0",
        )

        # Create transactions with different protocols
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
        Transaction.objects.create(
            dataset=dataset,
            source_city=city1,
            destination_city=city2,
            protocol="UDP",
            packet_count=50,
            bandwidth=500.0,
            latency=50.5,
            timestamp=timezone.now(),
        )

        builder = GraphBuilder()
        result = builder.build_from_city_pairs(
            source_city_id=city1.id,
            destination_city_id=city2.id,
            protocol="TCP",
        )

        assert result["transaction_count"] == 1

    def test_get_graph(self, db):
        """Test getting the graph backend."""
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
            dataset_name="Get Graph Dataset",
            version="1.0.0",
        )

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

        builder = GraphBuilder()
        builder.build_from_dataset(dataset.id)

        graph = builder.get_graph()
        assert isinstance(graph, NetworkXBackend)
        assert graph.get_node_count() == 2
        assert graph.get_edge_count() == 1

    def test_reset_clears_graph(self, db):
        """Test that reset clears all nodes and edges."""
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
            dataset_name="Reset Dataset",
            version="1.0.0",
        )

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

        builder = GraphBuilder()
        builder.build_from_dataset(dataset.id)

        assert builder.backend.get_node_count() == 2
        assert builder.backend.get_edge_count() == 1

        builder.reset()

        assert builder.backend.get_node_count() == 0
        assert builder.backend.get_edge_count() == 0

    def test_build_with_bidirectional_traffic(self, db):
        """Test building graph with bidirectional traffic."""
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
            dataset_name="Bidirectional Dataset",
            version="1.0.0",
        )

        # Create traffic in both directions
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
            source_city=city2,
            destination_city=city1,
            protocol="TCP",
            packet_count=200,
            bandwidth=2000.0,
            latency=200.0,
            timestamp=timezone.now(),
        )

        builder = GraphBuilder()
        result = builder.build_from_dataset(dataset.id)

        assert result["transaction_count"] == 2
        assert result["node_count"] == 2
        assert result["edge_count"] == 2

    def test_edge_aggregation_with_same_city_different_protocols(self, db):
        """Test edge aggregation with different protocols."""
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
            dataset_name="Protocol Aggregation Dataset",
            version="1.0.0",
        )

        # Create transactions with different protocols
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
            protocol="UDP",
            packet_count=200,
            bandwidth=2000.0,
            latency=200.0,
            timestamp=timezone.now(),
        )

        builder = GraphBuilder()
        builder.build_from_dataset(dataset.id)

        edge_attrs = builder.backend.get_edge_attributes(str(city1.id), str(city2.id))
        assert edge_attrs is not None
        # Protocol may be either TCP or UDP (last one processed)
        assert edge_attrs["protocol"] in ["TCP", "UDP"]
        # Bandwidth and packet count should be aggregated
        assert edge_attrs["bandwidth"] == 3000.0
        assert edge_attrs["packet_count"] == 300
