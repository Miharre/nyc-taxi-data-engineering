CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS analytics;
CREATE SCHEMA IF NOT EXISTS meta;

CREATE TABLE IF NOT EXISTS meta.pipeline_runs (
  run_id UUID PRIMARY KEY,
  run_month TEXT NOT NULL,
  source_rows BIGINT NOT NULL,
  accepted_rows BIGINT NOT NULL,
  rejected_rows BIGINT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('success','failed')),
  error_message TEXT,
  started_at TIMESTAMPTZ NOT NULL,
  finished_at TIMESTAMPTZ NOT NULL
);
