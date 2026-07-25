"""
Unit Tests for Graph Engine Models.

This module contains unit tests for graph engine models.

Status: Phase 2 - Issue #1
"""

from django.core.exceptions import ValidationError
from django.utils import timezone

import pytest

from apps.graph_engine.models import City, Country, Dataset, Transaction


class TestCountryModel:
    """Tests for Country model."""

    def test_country_creation(self, db):
        """Test creating a country."""
        country = Country.objects.create(
            iso_code="US",
            country_name="United States",
            continent=Country.Continent.NORTH_AMERICA,
            latitude=37.0902,
            longitude=-95.7129,
        )
        assert country.id is not None
        assert country.iso_code == "US"
        assert country.country_name == "United States"

    def test_country_string_representation(self, db):
        """Test country string representation."""
        country = Country.objects.create(
            iso_code="US",
            country_name="United States",
            continent=Country.Continent.NORTH_AMERICA,
        )
        assert str(country) == "United States (US)"

    def test_country_unique_iso_code(self, db):
        """Test ISO code uniqueness."""
        Country.objects.create(
            iso_code="US",
            country_name="United States",
            continent=Country.Continent.NORTH_AMERICA,
        )
        with pytest.raises(Exception):
            Country.objects.create(
                iso_code="US",
                country_name="Different Name",
                continent=Country.Continent.NORTH_AMERICA,
            )


class TestCityModel:
    """Tests for City model."""

    def test_city_creation(self, db):
        """Test creating a city."""
        country = Country.objects.create(
            iso_code="US",
            country_name="United States",
            continent=Country.Continent.NORTH_AMERICA,
        )
        city = City.objects.create(
            country=country,
            city_name="New York",
            latitude=40.7128,
            longitude=-74.0060,
            population=8419000,
            timezone="America/New_York",
        )
        assert city.id is not None
        assert city.city_name == "New York"
        assert city.country == country

    def test_city_string_representation(self, db):
        """Test city string representation."""
        country = Country.objects.create(
            iso_code="US",
            country_name="United States",
            continent=Country.Continent.NORTH_AMERICA,
        )
        city = City.objects.create(
            country=country,
            city_name="New York",
            latitude=40.7128,
            longitude=-74.0060,
        )
        assert str(city) == "New York, United States"

    def test_city_coordinates_property(self, db):
        """Test city coordinates property."""
        country = Country.objects.create(
            iso_code="US",
            country_name="United States",
            continent=Country.Continent.NORTH_AMERICA,
        )
        city = City.objects.create(
            country=country,
            city_name="New York",
            latitude=40.7128,
            longitude=-74.0060,
        )
        coords = city.coordinates
        assert coords == (40.7128, -74.0060)

    def test_city_latitude_validation(self, db):
        """Test latitude validation constraints."""
        country = Country.objects.create(
            iso_code="US",
            country_name="United States",
            continent=Country.Continent.NORTH_AMERICA,
        )

        # Valid latitude
        city = City.objects.create(
            country=country,
            city_name="New York",
            latitude=40.7128,
            longitude=-74.0060,
        )
        assert city.latitude == 40.7128

        # Invalid latitude (> 90)
        with pytest.raises(Exception):
            City.objects.create(
                country=country,
                city_name="Invalid",
                latitude=91.0,
                longitude=0.0,
            )

    def test_city_longitude_validation(self, db):
        """Test longitude validation constraints."""
        country = Country.objects.create(
            iso_code="US",
            country_name="United States",
            continent=Country.Continent.NORTH_AMERICA,
        )

        # Valid longitude
        city = City.objects.create(
            country=country,
            city_name="New York",
            latitude=40.7128,
            longitude=-74.0060,
        )
        assert city.longitude == -74.0060

        # Invalid longitude (> 180)
        with pytest.raises(Exception):
            City.objects.create(
                country=country,
                city_name="Invalid",
                latitude=0.0,
                longitude=181.0,
            )


class TestDatasetModel:
    """Tests for Dataset model."""

    def test_dataset_creation(self, db):
        """Test creating a dataset."""
        dataset = Dataset.objects.create(
            dataset_name="Test Dataset",
            version="1.0.0",
            description="Test description",
            random_seed=42,
        )
        assert dataset.id is not None
        assert dataset.dataset_name == "Test Dataset"
        assert dataset.version == "1.0.0"
        assert dataset.status == Dataset.DatasetStatus.PENDING

    def test_dataset_string_representation(self, db):
        """Test dataset string representation."""
        dataset = Dataset.objects.create(
            dataset_name="Test Dataset",
            version="1.0.0",
        )
        assert str(dataset) == "Test Dataset v1.0.0"

    def test_dataset_unique_name_version(self, db):
        """Test unique constraint on name and version."""
        Dataset.objects.create(
            dataset_name="Test Dataset",
            version="1.0.0",
        )
        # Should be able to create same name with different version
        Dataset.objects.create(
            dataset_name="Test Dataset",
            version="1.1.0",
        )
        # Should NOT be able to create same name and version
        with pytest.raises(Exception):
            Dataset.objects.create(
                dataset_name="Test Dataset",
                version="1.0.0",
            )


class TestTransactionModel:
    """Tests for Transaction model."""

    def test_transaction_creation(self, db):
        """Test creating a transaction."""
        country1 = Country.objects.create(
            iso_code="US",
            country_name="United States",
            continent=Country.Continent.NORTH_AMERICA,
        )
        country2 = Country.objects.create(
            iso_code="GB",
            country_name="United Kingdom",
            continent=Country.Continent.EUROPE,
        )
        city1 = City.objects.create(
            country=country1,
            city_name="New York",
            latitude=40.7128,
            longitude=-74.0060,
        )
        city2 = City.objects.create(
            country=country2,
            city_name="London",
            latitude=51.5074,
            longitude=-0.1278,
        )
        dataset = Dataset.objects.create(
            dataset_name="Test Dataset",
            version="1.0.0",
        )
        transaction = Transaction.objects.create(
            dataset=dataset,
            source_city=city1,
            destination_city=city2,
            protocol=Transaction.Protocol.HTTPS,
            packet_count=100,
            bandwidth=1000.0,
            latency=100.5,
            timestamp=timezone.now(),
        )
        assert transaction.id is not None
        assert transaction.source_city == city1
        assert transaction.destination_city == city2

    def test_transaction_string_representation(self, db):
        """Test transaction string representation."""
        country1 = Country.objects.create(
            iso_code="US",
            country_name="United States",
            continent=Country.Continent.NORTH_AMERICA,
        )
        country2 = Country.objects.create(
            iso_code="GB",
            country_name="United Kingdom",
            continent=Country.Continent.EUROPE,
        )
        city1 = City.objects.create(
            country=country1,
            city_name="New York",
            latitude=40.7128,
            longitude=-74.0060,
        )
        city2 = City.objects.create(
            country=country2,
            city_name="London",
            latitude=51.5074,
            longitude=-0.1278,
        )
        dataset = Dataset.objects.create(
            dataset_name="Test Dataset",
            version="1.0.0",
        )
        transaction = Transaction.objects.create(
            dataset=dataset,
            source_city=city1,
            destination_city=city2,
            protocol=Transaction.Protocol.HTTPS,
            packet_count=100,
            bandwidth=1000.0,
            latency=100.5,
            timestamp=timezone.now(),
        )
        assert "New York" in str(transaction)
        assert "London" in str(transaction)
        assert "HTTPS" in str(transaction)

    def test_transaction_packet_count_positive(self, db):
        """Test packet count must be positive."""
        country1 = Country.objects.create(
            iso_code="US",
            country_name="United States",
            continent=Country.Continent.NORTH_AMERICA,
        )
        country2 = Country.objects.create(
            iso_code="GB",
            country_name="United Kingdom",
            continent=Country.Continent.EUROPE,
        )
        city1 = City.objects.create(
            country=country1,
            city_name="New York",
            latitude=40.7128,
            longitude=-74.0060,
        )
        city2 = City.objects.create(
            country=country2,
            city_name="London",
            latitude=51.5074,
            longitude=-0.1278,
        )
        dataset = Dataset.objects.create(
            dataset_name="Test Dataset",
            version="1.0.0",
        )

        # Valid packet count
        transaction = Transaction.objects.create(
            dataset=dataset,
            source_city=city1,
            destination_city=city2,
            protocol=Transaction.Protocol.HTTPS,
            packet_count=100,
            bandwidth=1000.0,
            latency=100.5,
            timestamp=timezone.now(),
        )
        assert transaction.packet_count == 100

        # Invalid packet count (zero)
        with pytest.raises(Exception):
            Transaction.objects.create(
                dataset=dataset,
                source_city=city1,
                destination_city=city2,
                protocol=Transaction.Protocol.HTTPS,
                packet_count=0,
                bandwidth=1000.0,
                latency=100.5,
                timestamp=timezone.now(),
            )
