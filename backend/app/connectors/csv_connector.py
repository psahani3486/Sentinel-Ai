"""
Sentinel AI — CSV Data Connector

Handles tabular CSV file sources with auto-detection of encoding and delimiter,
chunked streaming for large files, schema inference, and metadata extraction.
"""

import os
import time
from typing import Any, Generator

import pandas as pd

from app.connectors.base import BaseConnector
from app.core.exceptions import (
    ConfigurationError,
    ConnectionError,
    ReadError,
    SchemaDiscoveryError,
)


class CSVConnector(BaseConnector):
    """
    Data connector for local CSV files.

    Features:
    - Auto-detects delimiters (',', ';', '\t', '|')
    - Auto-detects encoding ('utf-8', 'latin-1', 'cp1252', 'ascii')
    - Streaming chunk reader for large files
    - Automatic schema and data type inference
    """

    SUPPORTED_DELIMITERS = [",", ";", "\t", "|"]
    SUPPORTED_ENCODINGS = ["utf-8", "latin-1", "cp1252", "ascii"]

    def __init__(self, config: dict[str, Any]) -> None:
        super().__init__(config)
        self.file_path: str = config.get("file_path", "")
        self.delimiter: str | None = config.get("delimiter")
        self.encoding: str | None = config.get("encoding")
        self._detected_delimiter: str = ","
        self._detected_encoding: str = "utf-8"

    def validate_configuration(self) -> list[str]:
        """Validate required configuration parameters."""
        errors: list[str] = []
        if not self.file_path:
            errors.append("Configuration missing required field 'file_path'")
        elif not os.path.exists(self.file_path):
            errors.append(f"File path '{self.file_path}' does not exist")
        elif not os.path.isfile(self.file_path):
            errors.append(f"Path '{self.file_path}' is not a regular file")
        return errors

    def connect(self) -> None:
        """Verify file exists and auto-detect encoding and delimiter."""
        errors = self.validate_configuration()
        if errors:
            raise ConfigurationError("CSV Connector validation failed", errors=errors)

        try:
            self._detected_encoding = self._detect_encoding()
            self._detected_delimiter = self._detect_delimiter()
            self._is_connected = True
        except Exception as e:
            self._is_connected = False
            raise ConnectionError(f"Failed to open CSV file '{self.file_path}': {str(e)}")

    def disconnect(self) -> None:
        """Reset connection state."""
        self._is_connected = False

    def test_connection(self) -> bool:
        """Test if the file can be opened and read."""
        try:
            if not self._is_connected:
                self.connect()
            with open(self.file_path, "r", encoding=self._detected_encoding) as f:
                f.read(100)
            return True
        except Exception:
            return False

    def _detect_encoding(self) -> str:
        """Detect file encoding from configured or supported encodings."""
        if self.encoding and self.encoding != "auto":
            return self.encoding

        for enc in self.SUPPORTED_ENCODINGS:
            try:
                with open(self.file_path, "r", encoding=enc) as f:
                    f.read(4096)
                return enc
            except (UnicodeDecodeError, UnicodeError):
                continue
        return "utf-8"

    def _detect_delimiter(self) -> str:
        """Detect CSV delimiter by scoring header sample counts."""
        if self.delimiter and self.delimiter != "auto":
            return self.delimiter

        encoding = self._detected_encoding or "utf-8"
        best_delim = ","
        max_cols = 0

        try:
            with open(self.file_path, "r", encoding=encoding) as f:
                sample_lines = [f.readline() for _ in range(5)]
                sample_text = "".join([line for line in sample_lines if line])

            for delim in self.SUPPORTED_DELIMITERS:
                lines = sample_text.strip().split("\n")
                if lines:
                    col_counts = [len(line.split(delim)) for line in lines if line]
                    if col_counts and col_counts[0] > max_cols:
                        max_cols = col_counts[0]
                        best_delim = delim
        except Exception:
            pass

        return best_delim

    def fetch_schema(self) -> list[dict[str, Any]]:
        """Extract schema and infer column types."""
        if not self._is_connected:
            self.connect()

        try:
            df_sample = pd.read_csv(
                self.file_path,
                sep=self._detected_delimiter,
                encoding=self._detected_encoding,
                nrows=500,
            )

            schema: list[dict[str, Any]] = []
            for idx, col_name in enumerate(df_sample.columns):
                dtype_str = str(df_sample[col_name].dtype)
                inferred_type = self._map_dtype(dtype_str)
                sample_vals = df_sample[col_name].dropna().head(3).tolist()

                # Cast sample values to native Python types
                sample_vals_clean = [
                    v.item() if hasattr(v, "item") else v for v in sample_vals
                ]

                schema.append(
                    {
                        "column_name": str(col_name).strip(),
                        "data_type": inferred_type,
                        "is_nullable": bool(df_sample[col_name].isnull().any()),
                        "is_primary_key": idx == 0 and df_sample[col_name].is_unique,
                        "position": idx,
                        "sample_values": sample_vals_clean,
                    }
                )
            return schema
        except Exception as e:
            raise SchemaDiscoveryError(f"Failed to infer schema for '{self.file_path}': {str(e)}")

    def _map_dtype(self, pandas_dtype: str) -> str:
        """Map pandas dtype string to generic SQL/data type."""
        dtype_lower = pandas_dtype.lower()
        if "int" in dtype_lower:
            return "integer"
        elif "float" in dtype_lower:
            return "float"
        elif "bool" in dtype_lower:
            return "boolean"
        elif "datetime" in dtype_lower:
            return "timestamp"
        return "string"

    def preview(self, limit: int = 50) -> list[dict[str, Any]]:
        """Fetch initial sample rows."""
        if not self._is_connected:
            self.connect()

        try:
            df = pd.read_csv(
                self.file_path,
                sep=self._detected_delimiter,
                encoding=self._detected_encoding,
                nrows=limit,
            )
            # Fill NaN with None for JSON serializability
            df_clean = df.where(pd.notnull(df), None)
            return df_clean.to_dict(orient="records")
        except Exception as e:
            raise ReadError(f"Failed to preview file '{self.file_path}': {str(e)}")

    def read(
        self, chunksize: int | None = None
    ) -> pd.DataFrame | Generator[pd.DataFrame, None, None]:
        """Read full dataset or stream chunks."""
        if not self._is_connected:
            self.connect()

        try:
            if chunksize and chunksize > 0:
                return pd.read_csv(
                    self.file_path,
                    sep=self._detected_delimiter,
                    encoding=self._detected_encoding,
                    chunksize=chunksize,
                )
            return pd.read_csv(
                self.file_path,
                sep=self._detected_delimiter,
                encoding=self._detected_encoding,
            )
        except Exception as e:
            raise ReadError(f"Failed to read file '{self.file_path}': {str(e)}")

    def get_metadata(self) -> dict[str, Any]:
        """Extract metadata about the CSV file."""
        if not self._is_connected:
            self.connect()

        try:
            file_stat = os.stat(self.file_path)
            file_size = file_stat.st_size

            # Count rows quickly
            row_count = 0
            with open(self.file_path, "r", encoding=self._detected_encoding) as f:
                row_count = sum(1 for _ in f) - 1  # subtract header

            df_sample = pd.read_csv(
                self.file_path,
                sep=self._detected_delimiter,
                encoding=self._detected_encoding,
                nrows=5,
            )
            column_count = len(df_sample.columns)

            return {
                "file_path": self.file_path,
                "file_size_bytes": file_size,
                "row_count": max(0, row_count),
                "column_count": column_count,
                "delimiter": self._detected_delimiter,
                "encoding": self._detected_encoding,
                "columns": list(df_sample.columns),
            }
        except Exception as e:
            raise ReadError(f"Failed to extract metadata for '{self.file_path}': {str(e)}")

    def health_check(self) -> dict[str, Any]:
        """Perform health check on the CSV file source."""
        start_time = time.time()
        is_healthy = self.test_connection()
        latency_ms = round((time.time() - start_time) * 1000, 2)

        return {
            "status": "healthy" if is_healthy else "unhealthy",
            "latency_ms": latency_ms,
            "details": {
                "file_path": self.file_path,
                "exists": os.path.exists(self.file_path),
                "encoding": self._detected_encoding,
                "delimiter": self._detected_delimiter,
            },
        }
