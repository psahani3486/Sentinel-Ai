"""
Sentinel AI — Industrial Sensor Data Connector

Specialized connector optimized for Industrial IoT and Smart Manufacturing datasets:
- AI4I 2020 Predictive Maintenance Dataset
- NASA Turbofan Engine Degradation Simulation Dataset
- SECOM Semiconductor Manufacturing Dataset

Extends CSVConnector to automatically classify sensor signals, process parameters,
timestamps, equipment IDs, targets, numeric features, and categorical features.
"""

from typing import Any

import pandas as pd

from app.connectors.csv_connector import CSVConnector
from app.core.exceptions import SchemaDiscoveryError


class IndustrialSensorConnector(CSVConnector):
    """
    Specialized Industrial IoT Sensor Connector.

    Automatically identifies and categorizes:
    - Sensor columns (temperatures, speeds, torque, vibration, voltage, pressure)
    - Target columns (machine failures, degradation, RUL, pass/fail quality labels)
    - Timestamp columns (time, cycle, date, timestamp)
    - Identifier columns (UDI, Product ID, Unit Number, Machine ID)
    - Numeric and categorical features
    """

    IDENTIFIER_KEYWORDS = ["udi", "unit", "product id", "product_id", "machine_id", "serial", "device_id"]
    TIMESTAMP_KEYWORDS = ["time", "timestamp", "date", "cycle", "datetime", "t_stamp"]
    TARGET_KEYWORDS = [
        "failure",
        "label",
        "target",
        "rul",
        "status",
        "fault",
        "pass_fail",
        "twf",
        "hdf",
        "pwf",
        "osf",
        "rnf",
    ]
    SENSOR_KEYWORDS = [
        "temp",
        "temperature",
        "speed",
        "rpm",
        "torque",
        "wear",
        "vibration",
        "pressure",
        "sensor",
        "signal",
        "s1",
        "s2",
        "s3",
        "setting",
        "flow",
        "current",
        "voltage",
    ]

    def __init__(self, config: dict[str, Any]) -> None:
        super().__init__(config)
        self.dataset_variant: str = config.get("dataset_variant", "auto")

    def fetch_schema(self) -> list[dict[str, Any]]:
        """Fetch base schema and enrich column metadata with Industrial IoT tags."""
        base_schema = super().fetch_schema()
        classified = self.classify_columns()

        for col in base_schema:
            col_name = col["column_name"].lower()
            role = "numeric_feature"

            if col_name in [c.lower() for c in classified["target_columns"]]:
                role = "target"
            elif col_name in [c.lower() for c in classified["timestamp_columns"]]:
                role = "timestamp"
            elif col_name in [c.lower() for c in classified["identifier_columns"]]:
                role = "identifier"
            elif col_name in [c.lower() for c in classified["sensor_columns"]]:
                role = "sensor"
            elif col_name in [c.lower() for c in classified["categorical_features"]]:
                role = "categorical_feature"

            col["industrial_role"] = role

        return base_schema

    def classify_columns(self) -> dict[str, list[str]]:
        """
        Classify dataset columns into Industrial IoT domains.

        Returns:
            Dict containing lists for:
            - identifier_columns
            - timestamp_columns
            - sensor_columns
            - target_columns
            - numeric_features
            - categorical_features
        """
        if not self._is_connected:
            self.connect()

        try:
            df_sample = pd.read_csv(
                self.file_path,
                sep=self._detected_delimiter,
                encoding=self._detected_encoding,
                nrows=100,
            )

            identifiers: list[str] = []
            timestamps: list[str] = []
            targets: list[str] = []
            sensors: list[str] = []
            numerics: list[str] = []
            categoricals: list[str] = []

            for col in df_sample.columns:
                col_str = str(col).strip()
                col_lower = col_str.lower()

                # Check data type
                is_numeric = pd.api.types.is_numeric_dtype(df_sample[col])

                # 1. Targets / Failure indicators (checked first to prevent false matches with identifiers)
                if any(kw in col_lower for kw in self.TARGET_KEYWORDS):
                    targets.append(col_str)
                # 2. Timestamps / Cycle Counters
                elif any(kw in col_lower for kw in self.TIMESTAMP_KEYWORDS):
                    timestamps.append(col_str)
                # 3. Identifiers
                elif any(kw in col_lower for kw in self.IDENTIFIER_KEYWORDS) or col_lower == "id":
                    identifiers.append(col_str)
                # 4. Sensor signals
                elif any(kw in col_lower for kw in self.SENSOR_KEYWORDS) or is_numeric:
                    sensors.append(col_str)

                # Type classification
                if is_numeric:
                    numerics.append(col_str)
                else:
                    categoricals.append(col_str)

            return {
                "identifier_columns": identifiers,
                "timestamp_columns": timestamps,
                "target_columns": targets,
                "sensor_columns": sensors,
                "numeric_features": numerics,
                "categorical_features": categoricals,
            }
        except Exception as e:
            raise SchemaDiscoveryError(f"Failed to classify sensor columns: {str(e)}")

    def get_metadata(self) -> dict[str, Any]:
        """Extract metadata enriched with Industrial IoT domain classifications."""
        base_meta = super().get_metadata()
        classifications = self.classify_columns()

        base_meta["industrial_classification"] = classifications
        base_meta["sensor_count"] = len(classifications["sensor_columns"])
        base_meta["target_count"] = len(classifications["target_columns"])
        base_meta["has_timestamp"] = len(classifications["timestamp_columns"]) > 0

        return base_meta
