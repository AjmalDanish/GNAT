"""
City Data Loader Service.

This module handles loading city data from external sources (CSV files).

Architecture:
- Clean Architecture: Service Layer
- Uses pandas for efficient CSV processing
- Async-suitable design

Status: Phase 2 - Issue #1
"""
import logging
from pathlib import Path
from typing import Optional

import pandas as pd

from apps.graph_engine.validators import CityValidator, CountryValidator

logger = logging.getLogger(__name__)


class CityDataLoader:
    """
    Service for loading city data from CSV files.

    This service:
    - Loads CSV files
    - Validates columns
    - Normalizes data
    - Returns pandas DataFrame

    Usage:
        loader = CityDataLoader()
        cities_df = loader.load_csv("data/cities.csv")
    """

    REQUIRED_COLUMNS = {"city", "country", "lat", "lon"}
    OPTIONAL_COLUMNS = {"population", "timezone"}

    def __init__(self) -> None:
        """Initialize the city data loader."""
        self.validator = CityValidator()
        self.country_validator = CountryValidator()

    def load_csv(
        self, file_path: Path | str, encoding: str = "utf-8"
    ) -> pd.DataFrame:
        """
        Load cities from CSV file.

        Args:
            file_path: Path to CSV file.
            encoding: File encoding.

        Returns:
            DataFrame containing city data.

        Raises:
            FileNotFoundError: If file doesn't exist.
            ValueError: If required columns are missing.
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"City data file not found: {file_path}")

        logger.info(f"Loading city data from {file_path}")

        df = pd.read_csv(file_path, encoding=encoding, low_memory=False)

        # Validate required columns
        self._validate_columns(df.columns.tolist())

        logger.info(f"Loaded {len(df)} cities from CSV")

        return df

    def _validate_columns(self, columns: list[str]) -> None:
        """
        Validate that required columns are present.

        Args:
            columns: List of column names.

        Raises:
            ValueError: If required columns are missing.
        """
        missing = self.REQUIRED_COLUMNS - set(columns)
        if missing:
            raise ValueError(
                f"Missing required columns in city data: {missing}. "
                f"Required: {self.REQUIRED_COLUMNS}"
            )

    def normalize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize and clean the city data DataFrame.

        This includes:
        - Standardizing column names
        - Removing duplicates
        - Normalizing city names
        - Handling missing values

        Args:
            df: Raw city data DataFrame.

        Returns:
            Normalized DataFrame.
        """
        logger.info("Normalizing city data")

        # Standardize column names
        column_mapping = {
            "city": "city_name",
            "country": "country_name",
            "lat": "latitude",
            "lon": "longitude",
            "pop": "population",
            "tz": "timezone",
        }
        df = df.rename(columns=column_mapping)

        # Remove duplicates based on city_name and country_name
        initial_count = len(df)
        df = df.drop_duplicates(subset=["city_name", "country_name"], keep="first")
        duplicates_removed = initial_count - len(df)

        if duplicates_removed > 0:
            logger.info(f"Removed {duplicates_removed} duplicate cities")

        # Remove rows with missing essential data
        df = df.dropna(subset=["city_name", "country_name", "latitude", "longitude"])

        # Normalize city names (title case, trim)
        df["city_name"] = df["city_name"].str.strip().str.title()
        df["country_name"] = df["country_name"].str.strip().str.title()

        logger.info(f"Normalized city data: {len(df)} cities remaining")

        return df

    def validate_dataframe(self, df: pd.DataFrame) -> list[str]:
        """
        Validate all city data in the DataFrame.

        Args:
            df: DataFrame to validate.

        Returns:
            List of validation error messages.
        """
        logger.info("Validating city data")

        errors = []

        for idx, row in df.iterrows():
            try:
                # Validate city name
                self.validator.validate_city_name(row.get("city_name"))

                # Validate coordinates
                self.validator.validate_latitude(row.get("latitude"))
                self.validator.validate_longitude(row.get("longitude"))

                # Validate optional fields if present
                if "population" in row and pd.notna(row["population"]):
                    self.validator.validate_population(row["population"])

                if "timezone" in row and pd.notna(row["timezone"]):
                    self.validator.validate_timezone(row["timezone"])

            except Exception as e:
                errors.append(f"Row {idx}: {e}")

        if errors:
            logger.warning(f"Found {len(errors)} validation errors")

        return errors

    def load_and_process(self, file_path: Path | str) -> tuple[pd.DataFrame, list[str]]:
        """
        Load, normalize, and validate city data from CSV.

        This is a convenience method that combines all processing steps.

        Args:
            file_path: Path to CSV file.

        Returns:
            Tuple of (processed DataFrame, list of validation errors).
        """
        df = self.load_csv(file_path)
        df = self.normalize_dataframe(df)
        errors = self.validate_dataframe(df)

        return df, errors