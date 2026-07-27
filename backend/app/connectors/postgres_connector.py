"""
Sentinel AI — PostgreSQL Data Connector

Provides SQL database schema discovery, table inspection, connection health testing,
and data streaming for PostgreSQL relational databases.
"""

import time
from typing import Any, Generator

import pandas as pd
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine

from app.connectors.base import BaseConnector
from app.core.exceptions import (
    ConfigurationError,
    ConnectionError,
    ReadError,
    SchemaDiscoveryError,
)


class PostgreSQLConnector(BaseConnector):
    """
    Data connector for PostgreSQL databases.

    Features:
    - Connection testing and health diagnostics
    - Dynamic schema and table discovery
    - Preview sampling and chunked query streaming
    """

    def __init__(self, config: dict[str, Any]) -> None:
        super().__init__(config)
        self.host: str = config.get("host", "localhost")
        self.port: int = int(config.get("port", 5432))
        self.database: str = config.get("database", "")
        self.username: str = config.get("username", "")
        self.password: str = config.get("password", "")
        self.schema_name: str = config.get("schema_name", "public")
        self.table_name: str | None = config.get("table_name")
        self._engine: Engine | None = None

    def validate_configuration(self) -> list[str]:
        """Validate required PostgreSQL parameters."""
        errors: list[str] = []
        if not self.host:
            errors.append("Configuration missing required field 'host'")
        if not self.port or self.port <= 0 or self.port > 65535:
            errors.append(f"Invalid port '{self.port}'")
        if not self.database:
            errors.append("Configuration missing required field 'database'")
        if not self.username:
            errors.append("Configuration missing required field 'username'")
        return errors

    def _build_connection_string(self) -> str:
        """Construct PostgreSQL connection URI."""
        return f"postgresql+psycopg2://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"

    def connect(self) -> None:
        """Create SQLAlchemy connection engine."""
        errors = self.validate_configuration()
        if errors:
            raise ConfigurationError("PostgreSQL Connector validation failed", errors=errors)

        try:
            conn_str = self._build_connection_string()
            self._engine = create_engine(conn_str, pool_pre_ping=True)
            # Test ping
            with self._engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            self._is_connected = True
        except Exception as e:
            self._is_connected = False
            raise ConnectionError(f"Failed to connect to PostgreSQL at '{self.host}:{self.port}': {str(e)}")

    def disconnect(self) -> None:
        """Dispose connection engine."""
        if self._engine:
            self._engine.dispose()
            self._engine = None
        self._is_connected = False

    def test_connection(self) -> bool:
        """Test PostgreSQL database connection."""
        try:
            if not self._is_connected or not self._engine:
                self.connect()
            else:
                with self._engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
            return True
        except Exception:
            return False

    def list_tables(self) -> list[str]:
        """List all tables available in the configured schema."""
        if not self._is_connected or not self._engine:
            self.connect()

        try:
            inspector = inspect(self._engine)
            return inspector.get_table_names(schema=self.schema_name)
        except Exception as e:
            raise SchemaDiscoveryError(f"Failed to list tables in schema '{self.schema_name}': {str(e)}")

    def fetch_schema(self) -> list[dict[str, Any]]:
        """Discover table schema, column data types, and primary keys."""
        if not self.table_name:
            raise ConfigurationError("Cannot fetch schema without a specified 'table_name'")
        if not self._is_connected or not self._engine:
            self.connect()

        try:
            inspector = inspect(self._engine)
            columns = inspector.get_columns(self.table_name, schema=self.schema_name)
            pk_constraint = inspector.get_pk_constraint(self.table_name, schema=self.schema_name)
            pk_cols = pk_constraint.get("constrained_columns", []) if pk_constraint else []

            schema: list[dict[str, Any]] = []
            for idx, col in enumerate(columns):
                schema.append(
                    {
                        "column_name": col["name"],
                        "data_type": str(col["type"]).lower(),
                        "is_nullable": col.get("nullable", True),
                        "is_primary_key": col["name"] in pk_cols,
                        "position": idx,
                        "sample_values": [],
                    }
                )
            return schema
        except Exception as e:
            raise SchemaDiscoveryError(f"Failed to fetch schema for table '{self.table_name}': {str(e)}")

    def preview(self, limit: int = 50) -> list[dict[str, Any]]:
        """Fetch sample rows from the database table."""
        if not self.table_name:
            raise ConfigurationError("Cannot preview data without a specified 'table_name'")
        if not self._is_connected or not self._engine:
            self.connect()

        try:
            query = f"SELECT * FROM {self.schema_name}.{self.table_name} LIMIT {limit}"
            df = pd.read_sql(query, self._engine)
            df_clean = df.where(pd.notnull(df), None)
            return df_clean.to_dict(orient="records")
        except Exception as e:
            raise ReadError(f"Failed to preview table '{self.table_name}': {str(e)}")

    def read(
        self, chunksize: int | None = None
    ) -> pd.DataFrame | Generator[pd.DataFrame, None, None]:
        """Query full dataset or stream chunks."""
        if not self.table_name:
            raise ConfigurationError("Cannot read data without a specified 'table_name'")
        if not self._is_connected or not self._engine:
            self.connect()

        try:
            query = f"SELECT * FROM {self.schema_name}.{self.table_name}"
            if chunksize and chunksize > 0:
                return pd.read_sql(query, self._engine, chunksize=chunksize)
            return pd.read_sql(query, self._engine)
        except Exception as e:
            raise ReadError(f"Failed to read table '{self.table_name}': {str(e)}")

    def get_metadata(self) -> dict[str, Any]:
        """Extract database table metadata."""
        if not self._is_connected or not self._engine:
            self.connect()

        try:
            tables = self.list_tables()
            row_count = 0
            col_count = 0

            if self.table_name:
                with self._engine.connect() as conn:
                    res = conn.execute(text(f"SELECT COUNT(*) FROM {self.schema_name}.{self.table_name}"))
                    row_count = res.scalar_one()
                schema_cols = self.fetch_schema()
                col_count = len(schema_cols)

            return {
                "connector": "postgresql",
                "host": self.host,
                "port": self.port,
                "database": self.database,
                "schema": self.schema_name,
                "table_name": self.table_name,
                "available_tables": tables,
                "row_count": row_count,
                "column_count": col_count,
            }
        except Exception as e:
            raise ReadError(f"Failed to extract PostgreSQL metadata: {str(e)}")

    def health_check(self) -> dict[str, Any]:
        """Perform health check on the PostgreSQL endpoint."""
        start_time = time.time()
        is_healthy = self.test_connection()
        latency_ms = round((time.time() - start_time) * 1000, 2)

        return {
            "status": "healthy" if is_healthy else "unhealthy",
            "latency_ms": latency_ms,
            "details": {
                "host": self.host,
                "port": self.port,
                "database": self.database,
                "connected": self._is_connected,
            },
        }
