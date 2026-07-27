"""
Sentinel AI — Connector Factory

Implements Factory and Strategy patterns for connector instantiation.
Maps ConnectorType enum values directly to concrete BaseConnector subclasses
without conditional branching.
"""

from typing import Any

from app.connectors.base import BaseConnector
from app.connectors.csv_connector import CSVConnector
from app.connectors.mysql_connector import MySQLConnector
from app.connectors.postgres_connector import PostgreSQLConnector
from app.connectors.sensor_connector import IndustrialSensorConnector
from app.core.exceptions import ConfigurationError
from app.models.enums import ConnectorType


class ConnectorFactory:
    """
    Factory for instantiating data connectors dynamically.

    Registry maps ConnectorType enum values to implementation classes.
    """

    _registry: dict[ConnectorType, type[BaseConnector]] = {
        ConnectorType.CSV: CSVConnector,
        ConnectorType.INDUSTRIAL_SENSOR: IndustrialSensorConnector,
        ConnectorType.POSTGRESQL: PostgreSQLConnector,
        ConnectorType.MYSQL: MySQLConnector,
    }

    @classmethod
    def register(cls, connector_type: ConnectorType, connector_cls: type[BaseConnector]) -> None:
        """
        Dynamically register a new connector class (enabling plugin architecture).

        Args:
            connector_type: ConnectorType enum value.
            connector_cls: Concrete BaseConnector subclass.
        """
        cls._registry[connector_type] = connector_cls

    @classmethod
    def create(cls, connector_type: ConnectorType | str, config: dict[str, Any]) -> BaseConnector:
        """
        Instantiate and return the appropriate connector instance.

        Args:
            connector_type: ConnectorType enum or valid string representation.
            config: Configuration dictionary for the connector.

        Returns:
            Instance of concrete BaseConnector subclass.

        Raises:
            ConfigurationError: If connector_type is unknown or unregistered.
        """
        if isinstance(connector_type, str):
            try:
                connector_type = ConnectorType(connector_type.lower())
            except ValueError:
                raise ConfigurationError(
                    f"Unsupported connector type '{connector_type}'. Supported types: {[c.value for c in ConnectorType]}"
                )

        connector_cls = cls._registry.get(connector_type)
        if not connector_cls:
            raise ConfigurationError(
                f"No connector registered for type '{connector_type.value}'. Supported: {[c.value for c in cls._registry]}"
            )

        return connector_cls(config)

    @classmethod
    def get_supported_connectors(cls) -> list[str]:
        """Return list of supported connector type string identifiers."""
        return [c.value for c in cls._registry.keys()]
