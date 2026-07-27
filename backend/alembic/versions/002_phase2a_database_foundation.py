"""phase2a_database_foundation

Revision ID: 002_phase2a_database_foundation
Revises: 001_initial_schema
Create Date: 2026-07-26 13:48:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '002_phase2a_database_foundation'
down_revision: Union[str, None] = '001_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── Create Enums ──────────────────────────────────────────────────────────
    dataset_type_enum = postgresql.ENUM('tabular', 'time_series', 'sensor_stream', 'unstructured', name='dataset_type', create_type=False)
    connector_type_enum = postgresql.ENUM('csv', 'postgresql', 'mysql', 'industrial_sensor', 'kafka', 's3', name='connector_type', create_type=False)
    validation_severity_enum = postgresql.ENUM('critical', 'high', 'medium', 'low', 'info', name='validation_severity', create_type=False)
    validation_status_enum = postgresql.ENUM('passed', 'warning', 'failed', 'error', 'skipped', name='validation_status', create_type=False)
    run_status_enum = postgresql.ENUM('pending', 'running', 'completed', 'failed', 'cancelled', name='run_status', create_type=False)
    rule_type_enum = postgresql.ENUM(
        'missing_values', 'duplicate_rows', 'invalid_timestamps', 'invalid_numeric_values',
        'negative_sensor_values', 'outliers', 'invalid_sensor_range', 'constant_columns',
        'high_cardinality', 'low_cardinality', 'null_columns', 'duplicate_columns',
        'wrong_data_types', 'schema_changes', 'freshness_validation', 'primary_key_validation',
        'unique_constraint_validation', 'column_statistics', 'data_completeness',
        'data_consistency', 'data_accuracy',
        name='rule_type', create_type=False
    )

    sa.Enum('tabular', 'time_series', 'sensor_stream', 'unstructured', name='dataset_type').create(op.get_bind(), checkfirst=True)
    sa.Enum('csv', 'postgresql', 'mysql', 'industrial_sensor', 'kafka', 's3', name='connector_type').create(op.get_bind(), checkfirst=True)
    sa.Enum('critical', 'high', 'medium', 'low', 'info', name='validation_severity').create(op.get_bind(), checkfirst=True)
    sa.Enum('passed', 'warning', 'failed', 'error', 'skipped', name='validation_status').create(op.get_bind(), checkfirst=True)
    sa.Enum('pending', 'running', 'completed', 'failed', 'cancelled', name='run_status').create(op.get_bind(), checkfirst=True)
    sa.Enum(
        'missing_values', 'duplicate_rows', 'invalid_timestamps', 'invalid_numeric_values',
        'negative_sensor_values', 'outliers', 'invalid_sensor_range', 'constant_columns',
        'high_cardinality', 'low_cardinality', 'null_columns', 'duplicate_columns',
        'wrong_data_types', 'schema_changes', 'freshness_validation', 'primary_key_validation',
        'unique_constraint_validation', 'column_statistics', 'data_completeness',
        'data_consistency', 'data_accuracy',
        name='rule_type'
    ).create(op.get_bind(), checkfirst=True)

    # ── 1. Create datasets table ──────────────────────────────────────────────
    op.create_table(
        'datasets',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('dataset_type', dataset_type_enum, nullable=False),
        sa.Column('connector_type', connector_type_enum, nullable=False),
        sa.Column('connection_config', sa.JSON(), nullable=True),
        sa.Column('owner_id', sa.UUID(), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('owner_id', 'name', name='uq_datasets_owner_name')
    )
    op.create_index('ix_datasets_connector_type', 'datasets', ['connector_type'], unique=False)
    op.create_index('ix_datasets_created_at', 'datasets', ['created_at'], unique=False)
    op.create_index('ix_datasets_is_active', 'datasets', ['is_active'], unique=False)
    op.create_index('ix_datasets_name', 'datasets', ['name'], unique=False)
    op.create_index('ix_datasets_owner_id', 'datasets', ['owner_id'], unique=False)

    # ── 2. Create dataset_versions table ─────────────────────────────────────
    op.create_table(
        'dataset_versions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('dataset_id', sa.UUID(), nullable=False),
        sa.Column('version_number', sa.Integer(), nullable=False),
        sa.Column('storage_path', sa.String(length=512), nullable=False),
        sa.Column('row_count', sa.BigInteger(), nullable=False),
        sa.Column('column_count', sa.Integer(), nullable=False),
        sa.Column('file_size_bytes', sa.BigInteger(), nullable=False),
        sa.Column('checksum', sa.String(length=64), nullable=True),
        sa.Column('ingested_by_id', sa.UUID(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['dataset_id'], ['datasets.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['ingested_by_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('dataset_id', 'version_number', name='uq_dataset_versions_dataset_version')
    )
    op.create_index('ix_dataset_versions_dataset_id', 'dataset_versions', ['dataset_id'], unique=False)

    # ── 3. Create dataset_schemas table ──────────────────────────────────────
    op.create_table(
        'dataset_schemas',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('dataset_version_id', sa.UUID(), nullable=False),
        sa.Column('column_count', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['dataset_version_id'], ['dataset_versions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('dataset_version_id')
    )
    op.create_index('ix_dataset_schemas_version_id', 'dataset_schemas', ['dataset_version_id'], unique=False)

    # ── 4. Create dataset_columns table ──────────────────────────────────────
    op.create_table(
        'dataset_columns',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('dataset_schema_id', sa.UUID(), nullable=False),
        sa.Column('column_name', sa.String(length=255), nullable=False),
        sa.Column('data_type', sa.String(length=64), nullable=False),
        sa.Column('is_nullable', sa.Boolean(), nullable=False),
        sa.Column('is_primary_key', sa.Boolean(), nullable=False),
        sa.Column('position', sa.Integer(), nullable=False),
        sa.Column('sample_values', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['dataset_schema_id'], ['dataset_schemas.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('dataset_schema_id', 'column_name', name='uq_dataset_columns_schema_name')
    )
    op.create_index('ix_dataset_columns_name', 'dataset_columns', ['column_name'], unique=False)
    op.create_index('ix_dataset_columns_schema_id', 'dataset_columns', ['dataset_schema_id'], unique=False)

    # ── 5. Create dataset_profiles table ─────────────────────────────────────
    op.create_table(
        'dataset_profiles',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('dataset_version_id', sa.UUID(), nullable=False),
        sa.Column('total_rows', sa.BigInteger(), nullable=False),
        sa.Column('total_columns', sa.Integer(), nullable=False),
        sa.Column('memory_bytes', sa.BigInteger(), nullable=False),
        sa.Column('profile_data', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['dataset_version_id'], ['dataset_versions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('dataset_version_id')
    )
    op.create_index('ix_dataset_profiles_version_id', 'dataset_profiles', ['dataset_version_id'], unique=False)

    # ── 6. Create validation_rules table ────────────────────────────────────
    op.create_table(
        'validation_rules',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('rule_type', rule_type_enum, nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('severity', validation_severity_enum, nullable=False),
        sa.Column('parameters', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index('ix_validation_rules_is_active', 'validation_rules', ['is_active'], unique=False)
    op.create_index('ix_validation_rules_rule_type', 'validation_rules', ['rule_type'], unique=False)
    op.create_index('ix_validation_rules_severity', 'validation_rules', ['severity'], unique=False)

    # ── 7. Create validation_runs table ─────────────────────────────────────
    op.create_table(
        'validation_runs',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('dataset_id', sa.UUID(), nullable=False),
        sa.Column('dataset_version_id', sa.UUID(), nullable=False),
        sa.Column('status', run_status_enum, nullable=False),
        sa.Column('overall_score', sa.Float(), nullable=True),
        sa.Column('completeness_score', sa.Float(), nullable=True),
        sa.Column('consistency_score', sa.Float(), nullable=True),
        sa.Column('accuracy_score', sa.Float(), nullable=True),
        sa.Column('freshness_score', sa.Float(), nullable=True),
        sa.Column('execution_time_ms', sa.Float(), nullable=False),
        sa.Column('triggered_by_id', sa.UUID(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['dataset_id'], ['datasets.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['dataset_version_id'], ['dataset_versions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['triggered_by_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_validation_runs_created_at', 'validation_runs', ['created_at'], unique=False)
    op.create_index('ix_validation_runs_dataset_id', 'validation_runs', ['dataset_id'], unique=False)
    op.create_index('ix_validation_runs_dataset_version_id', 'validation_runs', ['dataset_version_id'], unique=False)
    op.create_index('ix_validation_runs_status', 'validation_runs', ['status'], unique=False)

    # ── 8. Create validation_results table ──────────────────────────────────
    op.create_table(
        'validation_results',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('validation_run_id', sa.UUID(), nullable=False),
        sa.Column('rule_id', sa.UUID(), nullable=True),
        sa.Column('rule_type', rule_type_enum, nullable=False),
        sa.Column('status', validation_status_enum, nullable=False),
        sa.Column('severity', validation_severity_enum, nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('affected_columns', sa.JSON(), nullable=True),
        sa.Column('affected_rows_count', sa.BigInteger(), nullable=False),
        sa.Column('execution_time_ms', sa.Float(), nullable=False),
        sa.Column('score_impact', sa.Float(), nullable=False),
        sa.Column('details', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['rule_id'], ['validation_rules.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['validation_run_id'], ['validation_runs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_validation_results_rule_id', 'validation_results', ['rule_id'], unique=False)
    op.create_index('ix_validation_results_run_id', 'validation_results', ['validation_run_id'], unique=False)
    op.create_index('ix_validation_results_severity', 'validation_results', ['severity'], unique=False)
    op.create_index('ix_validation_results_status', 'validation_results', ['status'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_validation_results_status', table_name='validation_results')
    op.drop_index('ix_validation_results_severity', table_name='validation_results')
    op.drop_index('ix_validation_results_run_id', table_name='validation_results')
    op.drop_index('ix_validation_results_rule_id', table_name='validation_results')
    op.drop_table('validation_results')

    op.drop_index('ix_validation_runs_status', table_name='validation_runs')
    op.drop_index('ix_validation_runs_dataset_version_id', table_name='validation_runs')
    op.drop_index('ix_validation_runs_dataset_id', table_name='validation_runs')
    op.drop_index('ix_validation_runs_created_at', table_name='validation_runs')
    op.drop_table('validation_runs')

    op.drop_index('ix_validation_rules_severity', table_name='validation_rules')
    op.drop_index('ix_validation_rules_rule_type', table_name='validation_rules')
    op.drop_index('ix_validation_rules_is_active', table_name='validation_rules')
    op.drop_table('validation_rules')

    op.drop_index('ix_dataset_profiles_version_id', table_name='dataset_profiles')
    op.drop_table('dataset_profiles')

    op.drop_index('ix_dataset_columns_schema_id', table_name='dataset_columns')
    op.drop_index('ix_dataset_columns_name', table_name='dataset_columns')
    op.drop_table('dataset_columns')

    op.drop_index('ix_dataset_schemas_version_id', table_name='dataset_schemas')
    op.drop_table('dataset_schemas')

    op.drop_index('ix_dataset_versions_dataset_id', table_name='dataset_versions')
    op.drop_table('dataset_versions')

    op.drop_index('ix_datasets_owner_id', table_name='datasets')
    op.drop_index('ix_datasets_name', table_name='datasets')
    op.drop_index('ix_datasets_is_active', table_name='datasets')
    op.drop_index('ix_datasets_created_at', table_name='datasets')
    op.drop_index('ix_datasets_connector_type', table_name='datasets')
    op.drop_table('datasets')
