export interface PluginInstallation {
  id: string;
  installed_at: string;
  installed_by: string;
  is_enabled: boolean;
  configuration?: Record<string, any>;
}

export interface Plugin {
  id: string;
  plugin_id: string;
  name: string;
  version: string;
  author: string;
  description: string;
  plugin_type: "connector" | "validation_rule" | "profiling" | "drift_detector" | "alert_rule" | "analyzer" | "recommendation" | "forecast" | "workflow" | "dashboard_widget";
  status: "discovered" | "validated" | "loaded" | "enabled" | "disabled" | "error" | "unloaded";
  entry_point: string;
  minimum_platform_version: string;
  permissions?: { permissions?: string[] };
  manifest_data?: Record<string, any>;
  created_at: string;
  installations: PluginInstallation[];
}
