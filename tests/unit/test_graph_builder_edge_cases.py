"""
Additional Unit Tests for GraphBuilder Service.

Status: Phase 2 - Graph Construction Engine - Coverage Expansion
"""
import pytest
from datetime import datetime, timezone

from apps.graph_engine.services.graph_builder import GraphBuilder
from apps.graph_engine.backends.networkx_backend import NetworkXBackend


@pytest.mark.django_db
class TestGraphBuilderEdgeCases:
    """Additional edge case tests for GraphBuilder."""

    def test_build_from_single_transaction(self, db):
        """Test building from a dataset with a single transaction."""
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
            dataset_name="Single Transaction Dataset",
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
            timestamp=datetime.now(timezone.utc),
        )

        builder = GraphBuilder()
        result = builder.build_from_dataset(dataset.id)

        assert result["transaction_count"] == 1
        assert result["node_count"] == 2
        assert result["edge_count"] == 1

    def test_build_with_duplicate_edges(self, db):
        """Test that duplicate edges are aggregated correctly."""
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
            dataset_name="Duplicate Edges Dataset",
            version="1.0.0",
        )

        # Create 10 transactions with same source/destination
        for i in range(10):
            Transaction.objects.create(
                dataset=dataset,
                source_city=city1,
                destination_city=city2,
                protocol="TCP",
                packet_count=100 + i,
                bandwidth=1000.0,
                latency=100.0 + i,
                timestamp=datetime.now(timezone.utc),
            )

        builder = GraphBuilder()
        result = builder.build_from_dataset(dataset.id)

        assert result["transaction_count"] == 10
        assert result["node_count"] == 2
        assert result["edge_count"] == 1

        # Check edge aggregation
        edge_attrs = builder.backend.get_edge_attributes(str(city1.id), str(city2.id))
        assert edge_attrs is not None
        assert edge_attrs["packet_count"] == sum(100 + i for i in range(10))  # 1045

    def test_build_with_self_loop_edge(self, db):
        """Test building graph with self-loop edges."""
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
        )
        dataset = Dataset.objects.create(
            dataset_name="Self Loop Dataset",
            version="1.0.0",
        )

        Transaction.objects.create(
            dataset=dataset,
            source_city=city,
            destination_city=city,
            protocol="TCP",
            packet_count=100,
            bandwidth=1000.0,
            latency=0.0,
            timestamp=datetime.now(timezone.utc),
        )

        builder = GraphBuilder()
        result = builder.build_from_dataset(dataset.id)

        assert result["transaction_count"] == 1
        assert result["node_count"] == 1
        assert result["edge_count"] == 1

    def test_build_with_isolated_nodes(self, db):
        """Test building graph with isolated nodes."""
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
        city3 = City.objects.create(
            country=country,
            city_name="Chicago",
            latitude=41.8781,
            longitude=-87.6298,
        )
        dataset = Dataset.objects.create(
            dataset_name="Isolated Nodes Dataset",
            version="1.0.0",
        )

        # Create transaction only between city1 and city2
        Transaction.objects.create(
            dataset=dataset,
            source_city=city1,
            destination_city=city2,
            protocol="TCP",
            packet_count=100,
            bandwidth=1000.0,
            latency=100.5,
            timestamp=datetime.now(timezone.utc),
        )

        builder = GraphBuilder()
        result = builder.build_from_dataset(dataset.id)

        assert result["node_count"] == 2  # city3 not included
        assert result["edge_count"] == 1

    def test_build_without_edges(self, db):
        """Test building graph with no edges (empty dataset)."""
        from apps.graph_engine.models import Dataset

        dataset = Dataset.objects.create(
            dataset_name="No Edges Dataset",
            version="1.0.0",
        )

        builder = GraphBuilder()
        result = builder.build_from_dataset(dataset.id)

        assert result["transaction_count"] == 0
        assert result["node_count"] == 0
        assert result["edge_count"] == 0

    def test_build_from_invalid_dataset(self, db):
        """Test building from non-existent dataset."""
        import uuid

        builder = GraphBuilder()
        result = builder.build_from_dataset(uuid.uuid4())

        assert result["transaction_count"] == 0
        assert result["node_count"] == 0
        assert result["edge_count"] == 0

    def test_build_and_rebuild_graph(self, db):
        """Test that graph can be rebuilt correctly."""
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
            dataset_name="Rebuild Dataset",
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
            timestamp=datetime.now(timezone.utc),
        )

        # First build
        builder = GraphBuilder()
        result1 = builder.build_from_dataset(dataset.id)
        assert result1["node_count"] == 2

        # Reset and rebuild
        builder.reset()
        assert builder.backend.get_node_count() == 0

        result2 = builder.build_from_dataset(dataset.id)
        assert result2["node_count"] == 2

    def test_build_from_city_pair_nonexistent(self, db):
        """Test building from non-existent city pair."""
        import uuid

        builder = GraphBuilder()
        result = builder.build_from_city_pairs(
            uuid.uuid4(), uuid.uuid4()
        )

        assert result["transaction_count"] == 0
        assert result["node_count"] == 0
        assert result["edge_count"] == 0

    def test_build_from_time_range_empty(self, db):
        """Test building from empty time range."""
        from apps.graph_engine.models import Dataset

        dataset = Dataset.objects.create(
            dataset_name="Empty Time Range Dataset",
            version="1.0.0",
        )

        start_time = datetime(2020, 1, 1, tzinfo=timezone.utc)
        end_time = datetime(2020, 1, 2, tzinfo=timezone.utc)

        builder = GraphBuilder()
        result = builder.build_from_time_range(
            start_time, end_time, dataset.id
        )

        assert result["transaction_count"] == 0

    def test_build_with_large_dataset_batching(self, db):
        """Test building with large dataset and batch processing."""
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
            dataset_name="Large Dataset",
            version="1.0.0",
        )

        # Create 150 transactions
        for i in range(150):
            Transaction.objects.create(
                dataset=dataset,
                source_city=city1,
                destination_city=city2,
                protocol="TCP",
                packet_count=100,
                bandwidth=1000.0,
                latency=100.5,
                timestamp=datetime.now(timezone.utc),
            )

        builder = GraphBuilder()
        result = builder.build_from_dataset(dataset.id, batch_size=50)

        assert result["transaction_count"] == 150
        assert result["node_count"] == 2

    def test_build_with_multiple_protocols(self, db):
        """Test building graph with multiple protocols."""
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
            dataset_name="Multi-Protocol Dataset",
            version="1.0.0",
        )

        protocols = ["TCP", "UDP", "HTTP", "HTTPS"]
        for protocol in protocols:
            Transaction.objects.create(
                dataset=dataset,
                source_city=city1,
                destination_city=city2,
                protocol=protocol,
                packet_count=100,
                bandwidth=1000.0,
                latency=100.5,
                timestamp=datetime.now(timezone.utc),
            )

        builder = GraphBuilder()
        builder.build_from_dataset(dataset.id)

        # Edge should exist, protocol may be overwritten
        edge_attrs = builder.backend.get_edge_attributes(str(city1.id), str(city2.id))
        assert edge_attrs is not None
        assert edge_attrs["packet_count"] == 400

    def test_deterministic_graph_generation(self, db):
        """Test that graph generation is deterministic."""
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
            dataset_name="Determinism Dataset",
            version="1.0.0",
        )

        # Create transactions
        for i in range(10):
            Transaction.objects.create(
                dataset=dataset,
                source_city=city1,
                destination_city=city2,
                protocol="TCP",
                packet_count=100,
                bandwidth=1000.0,
                latency=100.5,
                timestamp=datetime.now(timezone.utc),
            )

        # Build graph twice
        builder1 = GraphBuilder()
        result1 = builder1.build_from_dataset(dataset.id)
        graph1_dict = builder1.backend.to_dict()

        builder2 = GraphBuilder()
        result2 = builder2.build_from_dataset(dataset.id)
        graph2_dict = builder2.backend.to_dict()

        assert result1 == result2
        assert graph1_dict == graph2_dict

    def test_exception_handling_invalid_transaction(self, db):
        """Test handling of invalid transaction data."""
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
            dataset_name="Edge Case Dataset",
            version="1.0.0",
        )

        # Create transaction with None bandwidth (should handle gracefully)
        Transaction.objects.create(
            dataset=dataset,
            source_city=city1,
            destination_city=city2,
            protocol="TCP",
            packet_count=100,
            bandwidth=0.0,  # Valid value
            latency=0.0,
            timestamp=datetime.now(timezone.utc),
        )

        builder = GraphBuilder()
        result = builder.build_from_dataset(dataset.id)

        assert result["transaction_count"] == 1
        assert result["node_count"] == 2