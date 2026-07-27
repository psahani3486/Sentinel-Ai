"""
Sentinel AI — Phase 2B Connector Framework Unit & Integration Tests

Verifies CSVConnector auto-detection, IndustrialSensorConnector feature classification,
PostgreSQL & MySQL connector mocking, ConnectorFactory dynamic creation, and ConnectorService.
"""

import os
from unittest.mock import MagicMock, patch
import pandas as pd
import pytest

from app.connectors.csv_connector import CSVConnector
from app.connectors.factory import ConnectorFactory
from app.connectors.mysql_connector import MySQLConnector
from app.connectors.postgres_connector import PostgreSQLConnector
from app.connectors.sensor_connector import IndustrialSensorConnector
from app.core.exceptions import ConfigurationError, ConnectionError, ReadError, SchemaDiscoveryError
from app.models.enums import ConnectorType
from app.services.connector_service import ConnectorService


@pytest.fixture
def sample_ai4i_file() -> str:
    """Return path to sample AI4I 2020 dataset file."""
    base_dir = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(base_dir, "data", "samples", "ai4i2020.csv")


@pytest.fixture
def sample_turbofan_file() -> str:
    """Return path to sample NASA Turbofan dataset file."""
    base_dir = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(base_dir, "data", "samples", "nasa_turbofan.csv")


@pytest.fixture
def sample_secom_file() -> str:
    """Return path to sample SECOM dataset file."""
    base_dir = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(base_dir, "data", "samples", "secom.csv")


# ── 1. CSVConnector Unit Tests ────────────────────────────────────────────────

def test_csv_connector_validation_and_lifecycle(sample_ai4i_file: str) -> None:
    """Test CSVConnector validation, connection, preview, reading, and metadata."""
    connector = CSVConnector({"file_path": sample_ai4i_file})
    assert connector.validate_configuration() == []

    # Invalid path
    bad_connector = CSVConnector({"file_path": "/nonexistent/invalid.csv"})
    assert len(bad_connector.validate_configuration()) == 1
    with pytest.raises(ConfigurationError):
        bad_connector.connect()

    # Connection and lifecycle
    connector.connect()
    assert connector.test_connection() is True

    # Fetch Schema
    schema = connector.fetch_schema()
    assert len(schema) > 0
    assert any(col["column_name"] == "Rotational speed [rpm]" for col in schema)

    # Preview
    preview_rows = connector.preview(limit=5)
    assert len(preview_rows) == 5

    # Read Full DataFrame
    df = connector.read()
    assert len(df) == 16

    # Read Chunked DataFrame
    chunk_iter = connector.read(chunksize=5)
    chunks = list(chunk_iter)
    assert len(chunks) == 4

    # Metadata & Health
    metadata = connector.get_metadata()
    assert metadata["row_count"] == 16
    assert metadata["column_count"] == 14

    health = connector.health_check()
    assert health["status"] == "healthy"

    connector.disconnect()


def test_csv_connector_error_handling() -> None:
    """Test CSVConnector error handling for broken or unreadable files."""
    connector = CSVConnector({"file_path": __file__})
    assert connector.test_connection() is True

    # Bad read_csv error wrapping
    with patch("pandas.read_csv", side_effect=Exception("Read failure")):
        with pytest.raises(ReadError):
            connector.preview(10)

        with pytest.raises(ReadError):
            connector.read()

        with pytest.raises(SchemaDiscoveryError):
            connector.fetch_schema()


# ── 2. IndustrialSensorConnector Unit Tests ───────────────────────────────────

def test_industrial_sensor_connector_ai4i(sample_ai4i_file: str) -> None:
    """Verify IndustrialSensorConnector feature classification for AI4I 2020."""
    sensor_conn = IndustrialSensorConnector({"file_path": sample_ai4i_file})
    sensor_conn.connect()

    classifications = sensor_conn.classify_columns()
    assert "UDI" in classifications["identifier_columns"] or "Product ID" in classifications["identifier_columns"]
    assert "Machine failure" in classifications["target_columns"]
    assert any("Rotational speed" in c for c in classifications["sensor_columns"])

    metadata = sensor_conn.get_metadata()
    assert metadata["sensor_count"] > 0
    assert metadata["target_count"] > 0

    schema = sensor_conn.fetch_schema()
    target_col = next(c for c in schema if c["column_name"] == "Machine failure")
    assert target_col["industrial_role"] == "target"

    sensor_conn.disconnect()


def test_industrial_sensor_connector_turbofan(sample_turbofan_file: str) -> None:
    """Verify IndustrialSensorConnector feature classification for NASA Turbofan."""
    sensor_conn = IndustrialSensorConnector({"file_path": sample_turbofan_file})
    sensor_conn.connect()

    classifications = sensor_conn.classify_columns()
    assert "unit_number" in classifications["identifier_columns"]
    assert "time_cycles" in classifications["timestamp_columns"]
    assert "target_rul" in classifications["target_columns"]
    assert any("s1_fan_inlet_temp" in c for c in classifications["sensor_columns"])

    sensor_conn.disconnect()


def test_industrial_sensor_connector_secom(sample_secom_file: str) -> None:
    """Verify IndustrialSensorConnector feature classification for SECOM."""
    sensor_conn = IndustrialSensorConnector({"file_path": sample_secom_file})
    sensor_conn.connect()

    classifications = sensor_conn.classify_columns()
    assert "timestamp" in classifications["timestamp_columns"]
    assert "target_label" in classifications["target_columns"]
    assert any("sensor_0" in c for c in classifications["sensor_columns"])

    sensor_conn.disconnect()


# ── 3. PostgreSQL and MySQL Connectors Unit Tests (Mocked) ───────────────────

@patch("pandas.read_sql")
@patch("app.connectors.postgres_connector.create_engine")
@patch("app.connectors.postgres_connector.inspect")
def test_postgres_connector(mock_inspect: MagicMock, mock_create_engine: MagicMock, mock_read_sql: MagicMock) -> None:
    """Verify PostgreSQLConnector config validation, schema fetch, preview, and read using mocks."""
    # Test invalid config
    bad_pg = PostgreSQLConnector({"host": ""})
    assert len(bad_pg.validate_configuration()) > 0
    with pytest.raises(ConfigurationError):
        bad_pg.connect()

    # Test without table_name
    PostgreSQLConnector({
        "host": "localhost", "port": 5432, "database": "db", "username": "user", "password": "pass"
    })

    config = {
        "host": "localhost",
        "port": 5432,
        "database": "test_db",
        "username": "postgres",
        "password": "secret_password",
        "table_name": "sensor_logs",
    }
    pg_conn = PostgreSQLConnector(config)
    assert pg_conn.validate_configuration() == []

    # Mock DB Engine execution
    mock_engine = MagicMock()
    mock_create_engine.return_value = mock_engine
    mock_inspector = MagicMock()
    mock_inspect.return_value = mock_inspector

    mock_inspector.get_table_names.return_value = ["sensor_logs", "maintenance_events"]
    mock_inspector.get_columns.return_value = [
        {"name": "id", "type": "INTEGER", "nullable": False},
        {"name": "temperature", "type": "FLOAT", "nullable": True},
    ]
    mock_inspector.get_pk_constraint.return_value = {"constrained_columns": ["id"]}
    mock_read_sql.return_value = pd.DataFrame([{"id": 1, "temperature": 25.4}])

    pg_conn.connect()
    assert pg_conn.test_connection() is True

    tables = pg_conn.list_tables()
    assert "sensor_logs" in tables

    schema = pg_conn.fetch_schema()
    assert len(schema) == 2
    assert schema[0]["column_name"] == "id"
    assert schema[0]["is_primary_key"] is True

    preview = pg_conn.preview(10)
    assert len(preview) == 1

    df = pg_conn.read()
    assert isinstance(df, pd.DataFrame)

    health = pg_conn.health_check()
    assert health["status"] == "healthy"

    pg_conn.disconnect()


@patch("pandas.read_sql")
@patch("app.connectors.mysql_connector.create_engine")
@patch("app.connectors.mysql_connector.inspect")
def test_mysql_connector(mock_inspect: MagicMock, mock_create_engine: MagicMock, mock_read_sql: MagicMock) -> None:
    """Verify MySQLConnector config validation, schema fetch, preview, and read using mocks."""
    # Test invalid config
    bad_mysql = MySQLConnector({"host": ""})
    assert len(bad_mysql.validate_configuration()) > 0
    with pytest.raises(ConfigurationError):
        bad_mysql.connect()

    config = {
        "host": "mysql.internal",
        "port": 3306,
        "database": "manufacturing",
        "username": "root",
        "password": "mysql_password",
        "table_name": "telemetry",
    }
    mysql_conn = MySQLConnector(config)
    assert mysql_conn.validate_configuration() == []

    mock_engine = MagicMock()
    mock_create_engine.return_value = mock_engine
    mock_inspector = MagicMock()
    mock_inspect.return_value = mock_inspector

    mock_inspector.get_table_names.return_value = ["telemetry"]
    mock_inspector.get_columns.return_value = [
        {"name": "rpm", "type": "INT", "nullable": True},
    ]
    mock_inspector.get_pk_constraint.return_value = {"constrained_columns": []}
    mock_read_sql.return_value = pd.DataFrame([{"rpm": 1500}])

    mysql_conn.connect()
    tables = mysql_conn.list_tables()
    assert "telemetry" in tables

    schema = mysql_conn.fetch_schema()
    assert len(schema) == 1
    assert schema[0]["column_name"] == "rpm"

    preview = mysql_conn.preview(5)
    assert len(preview) == 1

    df = mysql_conn.read()
    assert isinstance(df, pd.DataFrame)

    health = mysql_conn.health_check()
    assert health["status"] == "healthy"

    mysql_conn.disconnect()


@patch("app.connectors.postgres_connector.create_engine")
def test_postgres_connector_errors(mock_create_engine: MagicMock) -> None:
    """Verify PostgreSQL error handling and missing table error cases."""
    pg = PostgreSQLConnector({"host": "h", "port": 5432, "database": "d", "username": "u", "password": "p"})
    
    # Missing table_name when fetching schema
    with pytest.raises(ConfigurationError):
        pg.fetch_schema()

    with pytest.raises(ConfigurationError):
        pg.preview(10)

    with pytest.raises(ConfigurationError):
        pg.read()

    # Connection error mock
    mock_create_engine.side_effect = Exception("DB Connection Refused")
    with pytest.raises(ConnectionError):
        pg.connect()


@patch("app.connectors.mysql_connector.create_engine")
def test_mysql_connector_errors(mock_create_engine: MagicMock) -> None:
    """Verify MySQL error handling and missing table error cases."""
    mysql = MySQLConnector({"host": "h", "port": 3306, "database": "d", "username": "u", "password": "p"})

    with pytest.raises(ConfigurationError):
        mysql.fetch_schema()

    with pytest.raises(ConfigurationError):
        mysql.preview(10)

    with pytest.raises(ConfigurationError):
        mysql.read()

    mock_create_engine.side_effect = Exception("MySQL Refused")
    with pytest.raises(ConnectionError):
        mysql.connect()


# ── 4. ConnectorFactory Unit Tests ───────────────────────────────────────────

def test_connector_factory(sample_ai4i_file: str) -> None:
    """Verify ConnectorFactory dynamic instantiation and error handling."""
    supported = ConnectorFactory.get_supported_connectors()
    assert "csv" in supported
    assert "industrial_sensor" in supported
    assert "postgresql" in supported
    assert "mysql" in supported

    # Create CSV Connector
    csv_conn = ConnectorFactory.create(ConnectorType.CSV, {"file_path": sample_ai4i_file})
    assert isinstance(csv_conn, CSVConnector)

    # Create Industrial Sensor Connector via string
    sensor_conn = ConnectorFactory.create("industrial_sensor", {"file_path": sample_ai4i_file})
    assert isinstance(sensor_conn, IndustrialSensorConnector)

    # Invalid connector type
    with pytest.raises(ConfigurationError):
        ConnectorFactory.create("unsupported_type", {})


# ── 5. ConnectorService Unit Tests ───────────────────────────────────────────

def test_connector_service(sample_ai4i_file: str) -> None:
    """Verify ConnectorService operational workflows."""
    service = ConnectorService()
    config = {"file_path": sample_ai4i_file}

    # Validate config
    errors = service.validate_connector_config(ConnectorType.CSV, config)
    assert errors == []

    # Test Connection
    success = service.test_connection(ConnectorType.CSV, config)
    assert success is True

    # Fetch Schema
    schema = service.fetch_schema(ConnectorType.CSV, config)
    assert len(schema) > 0

    # Preview
    preview = service.preview_dataset(ConnectorType.CSV, config, limit=3)
    assert len(preview) == 3

    # Metadata & Health
    metadata = service.fetch_metadata(ConnectorType.CSV, config)
    assert metadata["row_count"] == 16

    health = service.health_check(ConnectorType.CSV, config)
    assert health["status"] == "healthy"


def test_base_connector_direct() -> None:
    """Verify direct BaseConnector default behavior."""
    from app.connectors.base import BaseConnector

    class DummyConnector(BaseConnector):
        def connect(self) -> None: pass
        def disconnect(self) -> None: pass
        def test_connection(self) -> bool: return True
        def fetch_schema(self) -> list: return []
        def preview(self, limit: int = 50) -> list: return []
        def read(self, chunksize: int | None = None): return None
        def get_metadata(self) -> dict: return {}
        def validate_configuration(self) -> list: return []
        def health_check(self) -> dict: return {"status": "ok"}

    dummy = DummyConnector({"param": "value"})
    assert dummy.config["param"] == "value"
    assert dummy._is_connected is False
    dummy.connect()
    dummy.disconnect()

