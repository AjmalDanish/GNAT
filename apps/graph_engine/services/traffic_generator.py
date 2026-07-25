"""
Synthetic Traffic Generator Service.

This module generates synthetic network traffic data between cities.

Architecture:
- Clean Architecture: Service Layer
- Supports configurable traffic patterns
- Supports multiple protocols
- Supports anomaly injection

Status: Phase 2 - Issue #1
"""

import logging
from datetime import datetime, timedelta
from random import Random
from typing import Optional

import numpy as np
import pandas as pd

from apps.graph_engine.models import City, Dataset
from apps.graph_engine.validators import TransactionValidator

logger = logging.getLogger(__name__)


class TrafficPattern:
    """Traffic pattern configuration."""

    def __init__(
        self,
        name: str = "random",
        description: str = "Random traffic pattern",
        weight_factor: float = 1.0,
        latency_factor: float = 1.0,
    ) -> None:
        """Initialize traffic pattern."""
        self.name = name
        self.description = description
        self.weight_factor = weight_factor
        self.latency_factor = latency_factor


# Predefined traffic patterns
PATTERNS = {
    "random": TrafficPattern("random", "Random traffic", 1.0, 1.0),
    "business": TrafficPattern("business", "Business hours traffic", 2.0, 1.2),
    "regional": TrafficPattern("regional", "Regional preference", 3.0, 0.8),
    "international": TrafficPattern("international", "International traffic", 1.5, 2.0),
    "hub_based": TrafficPattern("hub_based", "Hub-based traffic", 4.0, 1.5),
}


class SyntheticTrafficGenerator:
    """
    Service for generating synthetic network traffic.

    This service:
    - Generates realistic network traffic between cities
    - Supports configurable traffic patterns
    - Supports multiple protocols
    - Supports anomaly injection
    - Returns pandas DataFrame

    Usage:
        generator = SyntheticTrafficGenerator()
        transactions = generator.generate(
            cities_queryset=City.objects.all(),
            num_transactions=10000,
            pattern="random"
        )
    """

    PROTOCOLS = [
        "HTTP",
        "HTTPS",
        "SSH",
        "FTP",
        "SMTP",
        "DNS",
        "TCP",
        "UDP",
        "ICMP",
    ]

    PROTOCOL_WEIGHTS = {
        "HTTPS": 0.40,
        "HTTP": 0.20,
        "TCP": 0.10,
        "UDP": 0.08,
        "DNS": 0.08,
        "SSH": 0.05,
        "SMTP": 0.04,
        "FTP": 0.03,
        "ICMP": 0.02,
    }

    def __init__(
        self,
        random_seed: Optional[int] = None,
        pattern: str = "random",
        anomaly_percentage: float = 0.05,
    ) -> None:
        """
        Initialize the synthetic traffic generator.

        Args:
            random_seed: Random seed for reproducibility.
            pattern: Traffic pattern name.
            anomaly_percentage: Percentage of transactions that are anomalies (0.0-1.0).
        """
        self.random_seed = random_seed
        self.rng = np.random.RandomState(random_seed)
        self.pattern = PATTERNS.get(pattern, PATTERNS["random"])
        self.anomaly_percentage = max(0.0, min(1.0, anomaly_percentage))
        self.validator = TransactionValidator()

        logger.info(
            f"Initialized traffic generator with pattern={pattern}, "
            f"seed={random_seed}, anomaly_pct={anomaly_percentage}"
        )

    def generate(
        self,
        cities_queryset,
        num_transactions: int = 1000,
        time_window_hours: int = 24,
    ) -> pd.DataFrame:
        """
        Generate synthetic network traffic transactions.

        Args:
            cities_queryset: Django queryset of City objects.
            num_transactions: Number of transactions to generate.
            time_window_hours: Time window in hours for transaction timestamps.

        Returns:
            DataFrame containing generated transactions.
        """
        logger.info(f"Generating {num_transactions} transactions")

        # Load cities into memory for efficient access
        cities = list(cities_queryset)
        if not cities:
            raise ValueError("No cities available for traffic generation")

        city_df = pd.DataFrame(
            [
                {
                    "id": str(city.id),
                    "city_name": city.city_name,
                    "country_id": str(city.country_id),
                    "population": city.population or 0,
                    "latitude": city.latitude,
                    "longitude": city.longitude,
                }
                for city in cities
            ]
        )

        # Calculate population weights
        city_df["weight"] = np.sqrt(city_df["population"] + 1)  # Square root to reduce skew
        city_df["weight"] = city_df["weight"] / city_df["weight"].sum()

        # Generate transaction data
        data = self._generate_transaction_data(city_df, num_transactions, time_window_hours)

        # Add anomalies
        if self.anomaly_percentage > 0:
            num_anomalies = int(num_transactions * self.anomaly_percentage)
            self._inject_anomalies(data, num_anomalies, city_df)

        df = pd.DataFrame(data)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values("timestamp").reset_index(drop=True)

        logger.info(f"Generated {len(df)} transactions")
        logger.info(
            f"Anomalies: {df['is_anomaly'].sum()} ({df['is_anomaly'].sum()/len(df)*100:.1f}%)"
        )

        return df

    def _generate_transaction_data(
        self,
        city_df: pd.DataFrame,
        num_transactions: int,
        time_window_hours: int,
    ) -> list[dict]:
        """
        Generate transaction data using configured pattern.

        Args:
            city_df: DataFrame of cities.
            num_transactions: Number of transactions.
            time_window_hours: Time window in hours.

        Returns:
            List of transaction dictionaries.
        """
        data = []

        # Calculate distances between all city pairs for realistic latency
        distances = self._calculate_distances(city_df)

        # Generate transactions
        for i in range(num_transactions):
            # Select source and destination
            if self.pattern.name == "regional":
                # Prefer same-country connections
                source, dest = self._select_regional_pair(city_df)
            elif self.pattern.name == "hub_based":
                # Prefer connections to/from hubs
                source, dest = self._select_hub_based_pair(city_df)
            else:
                # Random selection
                source, dest = self._select_random_pair(city_df)

            # Calculate metrics
            distance = distances[source]["destinations"][dest]["distance"]

            # Calculate latency based on distance with randomness
            base_latency = self._calculate_latency(distance)
            latency = max(0, base_latency + self.rng.normal(0, base_latency * 0.2))

            # Calculate bandwidth (using pattern weight factor)
            bandwidth = self._calculate_bandwidth(city_df.loc[source], city_df.loc[dest])

            # Select protocol based on weights
            protocol = self.rng.choice(
                self.PROTOCOLS,
                p=[self.PROTOCOL_WEIGHTS[p] for p in self.PROTOCOLS],
            )

            # Generate timestamp
            timestamp = self._generate_timestamp(time_window_hours)

            # Generate packet count
            packet_count = max(1, int(self.rng.exponential(50)))

            transaction = {
                "source_city_id": source,
                "destination_city_id": dest,
                "protocol": protocol,
                "packet_count": packet_count,
                "packet_size": 1500,  # Standard MTU
                "bandwidth": bandwidth,
                "latency": latency,
                "duration": self.rng.exponential(30),  # Exponential distribution
                "timestamp": timestamp,
                "is_anomaly": False,
                "connection_type": "CLIENT_SERVER",
                "encryption": protocol in ["HTTPS", "SSH"],
                "risk_label": "NORMAL",
            }

            data.append(transaction)

        return data

    def _calculate_distances(self, city_df: pd.DataFrame) -> dict:
        """
        Calculate distances between all city pairs.

        Uses Haversine formula for great-circle distance.

        Args:
            city_df: DataFrame of cities.

        Returns:
            Dictionary of distances between city pairs.
        """
        distances = {}

        for idx, source_row in city_df.iterrows():
            distances[idx] = {"city": source_row["city_name"], "destinations": {}}

            for _, dest_row in city_df.iterrows():
                if source_row["id"] == dest_row["id"]:
                    continue

                distance = self._haversine(
                    source_row["latitude"],
                    source_row["longitude"],
                    dest_row["latitude"],
                    dest_row["longitude"],
                )

                distances[idx]["destinations"][dest_row["id"]] = {"distance": distance}

        return distances

    def _haversine(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate great-circle distance between two points.

        Args:
            lat1: Latitude of point 1.
            lon1: Longitude of point 1.
            lat2: Latitude of point 2.
            lon2: Longitude of point 2.

        Returns:
            Distance in kilometers.
        """
        # Convert to radians
        lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])

        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
        c = 2 * np.arcsin(np.sqrt(a))

        # Earth's radius in kilometers
        r = 6371

        return c * r

    def _calculate_latency(self, distance_km: float) -> float:
        """
        Calculate realistic latency based on distance.

        Args:
            distance_km: Distance in kilometers.

        Returns:
            Latency in milliseconds.
        """
        # Base latency: 2ms per 100km (realistic for fiber optics)
        base_latency = (distance_km / 100) * 2 * self.pattern.latency_factor

        # Add minimum latency (processing time)
        min_latency = 5.0

        return max(min_latency, base_latency)

    def _calculate_bandwidth(self, source_row: pd.Series, dest_row: pd.Series) -> float:
        """
        Calculate bandwidth based on city populations.

        Args:
            source_row: Source city data.
            dest_row: Destination city data.

        Returns:
            Bandwidth in bytes per second.
        """
        # Bandwidth scales with geometric mean of populations
        source_pop = source_row["population"] or 1
        dest_pop = dest_row["population"] or 1

        # Geometric mean with minimum
        geo_mean = np.sqrt(source_pop * dest_pop)
        base_bandwidth = geo_mean * 0.01  # Bytes per second

        # Apply pattern weight factor
        bandwidth = base_bandwidth * self.pattern.weight_factor

        # Add randomness
        bandwidth = bandwidth * self.rng.uniform(0.5, 2.0)

        return max(1000.0, bandwidth)  # Minimum 1 KB/s

    def _generate_timestamp(self, time_window_hours: int) -> datetime:
        """
        Generate random timestamp within time window.

        Args:
            time_window_hours: Time window in hours.

        Returns:
            Random datetime within the window.
        """
        now = datetime.utcnow()
        offset_seconds = self.rng.randint(0, time_window_hours * 3600)
        return now - timedelta(seconds=offset_seconds)

    def _select_random_pair(self, city_df: pd.DataFrame) -> tuple[str, str]:
        """Select random source and destination (different cities)."""
        source_idx = self.rng.choice(city_df.index, p=city_df["weight"].values)
        dest_idx = self.rng.choice(city_df.index, p=city_df["weight"].values)

        # Ensure source != destination
        while source_idx == dest_idx:
            dest_idx = self.rng.choice(city_df.index, p=city_df["weight"].values)

        return city_df.loc[source_idx, "id"], city_df.loc[dest_idx, "id"]

    def _select_regional_pair(self, city_df: pd.DataFrame) -> tuple[str, str]:
        """Select source and destination, preferring same country."""
        # Pick random source
        source_idx = self.rng.choice(city_df.index, p=city_df["weight"].values)
        source_country = city_df.loc[source_idx, "country_id"]

        # Prefer same country
        same_country = city_df[city_df["country_id"] == source_country]

        if len(same_country) > 1:
            dest_idx = self.rng.choice(same_country.index)
        else:
            # Fall back to random
            dest_idx = self.rng.choice(city_df.index)

        # Ensure different cities
        while dest_idx == source_idx:
            dest_idx = self.rng.choice(city_df.index)

        return city_df.loc[source_idx, "id"], city_df.loc[dest_idx, "id"]

    def _select_hub_based_pair(self, city_df: pd.DataFrame) -> tuple[str, str]:
        """Select source and destination, preferring hub cities."""
        # Select top 10% by population as hubs
        city_df_copy = city_df.copy()
        city_df_copy["hub_score"] = city_df_copy["population"] * city_df_copy["population"]
        city_df_copy = city_df_copy.sort_values("hub_score", ascending=False)
        hub_indices = city_df_copy.head(max(1, len(city_df_copy) // 10)).index

        # 50% chance to involve a hub
        if self.rng.random() < 0.5:
            hub_idx = self.rng.choice(hub_indices)
            if self.rng.random() < 0.5:
                source_idx = hub_idx
                dest_idx = self.rng.choice(city_df.index)
            else:
                source_idx = self.rng.choice(city_df.index)
                dest_idx = hub_idx
        else:
            source_idx, dest_idx = self._select_random_pair(city_df)

        return city_df.loc[source_idx, "id"], city_df.loc[dest_idx, "id"]

    def _inject_anomalies(
        self, data: list[dict], num_anomalies: int, city_df: pd.DataFrame
    ) -> None:
        """
        Inject anomalies into transaction data.

        Anomaly types:
        - Traffic spike: Very high bandwidth
        - Impossible latency: Unrealistically high latency
        - Packet anomaly: Very high packet count

        Args:
            data: List of transaction dictionaries.
            num_anomalies: Number of anomalies to inject.
            city_df: DataFrame of cities.
        """
        anomaly_indices = self.rng.choice(len(data), num_anomalies, replace=False)

        for idx in anomaly_indices:
            transaction = data[idx]
            anomaly_type = self.rng.choice(["spike", "latency", "packets"])

            if anomaly_type == "spike":
                # Traffic spike: 10x bandwidth
                transaction["bandwidth"] *= 10
                transaction["risk_label"] = "HIGH"

            elif anomaly_type == "latency":
                # Impossible latency: 1000x expected latency
                transaction["latency"] *= 1000
                transaction["risk_label"] = "CRITICAL"

            elif anomaly_type == "packets":
                # Packet anomaly: 100x packet count
                transaction["packet_count"] *= 100
                transaction["risk_label"] = "MEDIUM"

            transaction["is_anomaly"] = True

        logger.info(f"Injected {num_anomalies} anomalies")
