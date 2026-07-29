"""
Graph Builder Service.

This module builds graphs from Transaction records using the configured backend.

Architecture:
- Clean Architecture: Application Layer
- Business logic for graph construction
- Works through GraphBackend interface

Status: Phase 2 - Graph Construction Engine
"""

import uuid

from django.utils import timezone

from ..backends.networkx_backend import NetworkXBackend
from ..interfaces.graph_backend import GraphBackend
from ..models import Transaction


class GraphBuilder:
    """Service for building graphs from transaction data."""

    def __init__(self, backend: GraphBackend | None = None) -> None:
        """Initialize GraphBuilder.

        Args:
            backend: GraphBackend instance (defaults to NetworkXBackend)
        """
        self.backend = backend or NetworkXBackend()

    def build_from_dataset(
        self,
        dataset_id: uuid.UUID,
        batch_size: int = 1000,
        include_anomalies: bool = False,
    ) -> dict[str, int]:
        """Build graph from all transactions in a dataset.

        Args:
            dataset_id: Dataset ID to build graph from
            batch_size: Number of transactions to process per batch
            include_anomalies: Whether to include anomalous transactions

        Returns:
            Dict with graph statistics:
                - node_count: Number of nodes in graph
                - edge_count: Number of edges in graph
                - transaction_count: Number of transactions processed
        """
        transactions = Transaction.objects.filter(dataset_id=dataset_id)

        if not include_anomalies:
            transactions = transactions.filter(is_anomaly=False)

        transaction_count = 0

        # Prefetch related data to minimize queries
        transactions = transactions.select_related(
            "source_city",
            "destination_city",
            "source_city__country",
            "destination_city__country",
        ).iterator(chunk_size=batch_size)

        for transaction in transactions:
            self._add_transaction_to_graph(transaction)
            transaction_count += 1

        return {
            "node_count": self.backend.get_node_count(),
            "edge_count": self.backend.get_edge_count(),
            "transaction_count": transaction_count,
        }

    def build_from_city_pairs(
        self,
        source_city_id: uuid.UUID,
        destination_city_id: uuid.UUID,
        protocol: str | None = None,
    ) -> dict[str, int]:
        """Build graph from transactions between two specific cities.

        Args:
            source_city_id: Source city ID
            destination_city_id: Destination city ID
            protocol: Filter by protocol (optional)

        Returns:
            Dict with graph statistics
        """
        transactions = Transaction.objects.filter(
            source_city_id=source_city_id,
            destination_city_id=destination_city_id,
        )

        if protocol:
            transactions = transactions.filter(protocol=protocol)

        transaction_count = 0
        transactions = transactions.select_related(
            "source_city",
            "destination_city",
            "source_city__country",
            "destination_city__country",
        ).iterator()

        for transaction in transactions:
            self._add_transaction_to_graph(transaction)
            transaction_count += 1

        return {
            "node_count": self.backend.get_node_count(),
            "edge_count": self.backend.get_edge_count(),
            "transaction_count": transaction_count,
        }

    def build_from_time_range(
        self,
        start_time: timezone.datetime,
        end_time: timezone.datetime,
        dataset_id: uuid.UUID | None = None,
    ) -> dict[str, int]:
        """Build graph from transactions within a time range.

        Args:
            start_time: Start of time range
            end_time: End of time range
            dataset_id: Optional dataset filter

        Returns:
            Dict with graph statistics
        """
        transactions = Transaction.objects.filter(
            timestamp__gte=start_time, timestamp__lte=end_time
        )

        if dataset_id:
            transactions = transactions.filter(dataset_id=dataset_id)

        transaction_count = 0
        transactions = transactions.select_related(
            "source_city",
            "destination_city",
            "source_city__country",
            "destination_city__country",
        ).iterator()

        for transaction in transactions:
            self._add_transaction_to_graph(transaction)
            transaction_count += 1

        return {
            "node_count": self.backend.get_node_count(),
            "edge_count": self.backend.get_edge_count(),
            "transaction_count": transaction_count,
        }

    def _add_transaction_to_graph(self, transaction: Transaction) -> None:
        """Add a single transaction to the graph.

        Args:
            transaction: Transaction instance
        """
        source_city = transaction.source_city
        dest_city = transaction.destination_city

        # Add source node
        self.backend.add_node(
            node_id=str(source_city.id),
            country=source_city.country.country_name,
            city=source_city.city_name,
            coordinates=(float(source_city.latitude), float(source_city.longitude)),
        )

        # Add destination node
        self.backend.add_node(
            node_id=str(dest_city.id),
            country=dest_city.country.country_name,
            city=dest_city.city_name,
            coordinates=(float(dest_city.latitude), float(dest_city.longitude)),
        )

        # Add edge (aggregate if edge already exists)
        existing_edge = self.backend.get_edge_attributes(
            str(source_city.id), str(dest_city.id)
        )

        if existing_edge:
            # Aggregate values
            self.backend.add_edge(
                str(source_city.id),
                str(dest_city.id),
                bandwidth=existing_edge.get("bandwidth", 0.0)
                + float(transaction.bandwidth),
                latency=(existing_edge.get("latency", 0.0) + float(transaction.latency))
                / 2,
                packet_count=existing_edge.get("packet_count", 0)
                + transaction.packet_count,
                protocol=transaction.protocol,
            )
        else:
            # New edge
            self.backend.add_edge(
                str(source_city.id),
                str(dest_city.id),
                bandwidth=float(transaction.bandwidth),
                latency=float(transaction.latency),
                packet_count=transaction.packet_count,
                protocol=transaction.protocol,
            )

    def get_graph(self) -> GraphBackend:
        """Return the constructed graph.

        Returns:
            GraphBackend instance
        """
        return self.backend

    def reset(self) -> None:
        """Clear the graph and start fresh."""
        self.backend.clear()
