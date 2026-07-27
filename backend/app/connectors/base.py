"""
Sentinel AI — Base Connector Contract

Defines the abstract interface that every data connector must implement.
Ensures consistency across CSV, Industrial Sensors, PostgreSQL, MySQL, and future sources.
"""

from abc import ABC, abstractmethod
from typing import Any, Generator

import pandas as pd


class BaseConnector(ABC):
    """
    Abstract Base Class for all Sentinel AI data connectors.

    Every connector must manage its connection lifecycle, configuration validation,
    schema discovery, data previewing, streaming, and metadata extraction.
    """

    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config
        self._is_connected = False

    @abstractmethod
    def connect(self) -> None:
        """
        Establish connection to the target data source.

        Raises:
            ConnectionError: If connection fails.
        """
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Close active connection and release underlying resources."""
        pass

    @abstractmethod
    def test_connection(self) -> bool:
        """
        Verify if the target resource is reachable and credentials are valid.

        Returns:
            True if connection test succeeds, False otherwise.
        """
        pass

    @abstractmethod
    def fetch_schema(self) -> list[dict[str, Any]]:
        """
        Discover columns, infer data types, nullability, and primary keys.

        Returns:
            List of column metadata dictionaries:
            [
                {
                    "column_name": str,
                    "data_type": str,
                    "is_nullable": bool,
                    "is_primary_key": bool,
                    "position": int,
                    "sample_values": list
                }, ...
            ]
        """
        pass

    @abstractmethod
    def preview(self, limit: int = 50) -> list[dict[str, Any]]:
        """
        Fetch sample rows from the data source as a list of dictionaries.

        Args:
            limit: Maximum number of rows to return (default 50).

        Returns:
            List of row record dictionaries.
        """
        pass

    @abstractmethod
    def read(
        self, chunksize: int | None = None
    ) -> pd.DataFrame | Generator[pd.DataFrame, None, None]:
        """
        Read dataset into a pandas DataFrame or yield DataFrames in chunks.

        Args:
            chunksize: Optional number of rows per chunk for streaming large files.

        Returns:
            Complete DataFrame or Generator of DataFrame chunks.
        """
        pass

    @abstractmethod
    def get_metadata(self) -> dict[str, Any]:
        """
        Extract summary metadata about the data resource.

        Returns:
            Dictionary containing row count, column count, size, encoding, etc.
        """
        pass

    @abstractmethod
    def validate_configuration(self) -> list[str]:
        """
        Validate connector configuration inputs.

        Returns:
            List of validation error strings. Empty list if configuration is valid.
        """
        pass

    @abstractmethod
    def health_check(self) -> dict[str, Any]:
        """
        Perform a health check returning operational status and metrics.

        Returns:
            Dict containing status ('healthy', 'unhealthy'), latency_ms, details.
        """
        pass
