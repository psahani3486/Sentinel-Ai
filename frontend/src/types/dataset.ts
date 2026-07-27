export type DatasetType = "tabular" | "time_series" | "sensor_stream" | "unstructured";

export type ConnectorType = "csv" | "postgresql" | "mysql" | "industrial_sensor" | "kafka" | "s3";

export interface DatasetVersion {
  id: string;
  version_number: number;
  storage_path: string;
  row_count?: number;
  column_count?: number;
  file_size_bytes?: number;
  created_at: string;
}

export interface DatasetItem {
  id: string;
  name: string;
  description?: string;
  dataset_type: DatasetType;
  connector_type: ConnectorType;
  is_active: boolean;
  active_version_id?: string;
  active_version?: DatasetVersion;
  created_at: string;
}

export interface DatasetsListResponse {
  items: DatasetItem[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

export interface ColumnSchema {
  column_name: string;
  data_type: string;
  is_nullable: boolean;
  is_primary_key: boolean;
}

export interface SchemaResponse {
  dataset_id: string;
  version_id: string;
  columns: ColumnSchema[];
}

export interface PreviewResponse {
  dataset_id: string;
  version_id: string;
  limit: number;
  rows: Record<string, any>[];
}

export interface ProfileResponse {
  dataset_id: string;
  version_id: string;
  profile: Record<string, any>;
}
