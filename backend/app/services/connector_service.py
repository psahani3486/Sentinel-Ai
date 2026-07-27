"""
Sentinel AI — Connector Service

Provides high-level business operations for connector validation, connection testing,
schema discovery, dataset previews, and metadata retrieval.
"""

import logging
from typing import Any

from app.connectors.base import BaseConnector
from app.connectors.factory import ConnectorFactory
from app.models.enums import ConnectorType

logger = logging.getLogger(__name__)


class ConnectorService:
    """Service layer for managing connector lifecycle and interactions."""

    def create_connector(
        self, connector_type: ConnectorType | str, config: dict[str, Any]
    ) -> BaseConnector:
        """Instantiate a connector using the ConnectorFactory."""
        connector = ConnectorFactory.create(connector_type, config)
        logger.info("Instantiated connector: %s", connector.__class__.__name__)
        return connector

    def validate_connector_config(
        self, connector_type: ConnectorType | str, config: dict[str, Any]
    ) -> list[str]:
        """Validate connector configuration parameters without connecting."""
        connector = self.create_connector(connector_type, config)
        return connector.validate_configuration()

    def test_connection(
        self, connector_type: ConnectorType | str, config: dict[str, Any]
    ) -> bool:
        """Test connection to target data source."""
        connector = self.create_connector(connector_type, config)
        try:
            connector.connect()
            success = connector.test_connection()
            return success
        finally:
            connector.disconnect()

    def fetch_schema(
        self, connector_type: ConnectorType | str, config: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Extract schema and data types from data source."""
        connector = self.create_connector(connector_type, config)
        try:
            connector.connect()
            return connector.fetch_schema()
        finally:
            connector.disconnect()

    def preview_dataset(
        self,
        connector_type: ConnectorType | str,
        config: dict[str, Any],
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Fetch sample rows from data source."""
        connector = self.create_connector(connector_type, config)
        try:
            connector.connect()
            return connector.preview(limit=limit)
        finally:
            connector.disconnect()

    def fetch_metadata(
        self, connector_type: ConnectorType | str, config: dict[str, Any]
    ) -> dict[str, Any]:
        """Fetch comprehensive metadata from data source."""
        connector = self.create_connector(connector_type, config)
        try:
            connector.connect()
            return connector.get_metadata()
        finally:
            connector.disconnect()

    def health_check(
        self, connector_type: ConnectorType | str, config: dict[str, Any]
    ) -> dict[str, Any]:
        """Perform health check on data source."""
        connector = self.create_connector(connector_type, config)
        try:
            return connector.health_check()
        finally:
            connector.disconnect()
