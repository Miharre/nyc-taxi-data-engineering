# Architecture

```mermaid
flowchart LR
    A[NYC TLC monthly Parquet] --> B[Python extract]
    Z[Taxi zone lookup CSV] --> B
    B --> C[Transform + validate]
    C -->|accepted| S[(raw.stg_yellow_trips)]
    C -->|rejected| Q[(raw.rejected_yellow_trips)]
    S --> F[(analytics.fact_trips)]
    Z --> D[(analytics.dim_location)]
    F --> G[SQL quality gates]
    D --> G
    G --> V[Analytics views]
    V --> BI[BI client]
    R[(meta.pipeline_runs)] -. run audit .-> B
    AF[Airflow DAG example] -. schedules same entry point .-> B
    CI[GitHub Actions] -. tests .-> C
```

## Data flow

The Python entry point owns one end-to-end run. It downloads/caches source files, transforms records, attaches a run ID, writes accepted rows to run-scoped staging, appends rejected rows to quarantine, refreshes the taxi-zone lookup, builds the warehouse, creates analytics views, executes SQL quality gates, and only then records the run as successful.

A failure after metadata initialization is recorded as a failed run and re-raised so the process exits non-zero.

## Engineering choices

- Parquet remains the source format instead of being expanded to CSV.
- PostgreSQL provides a reproducible local warehouse with `raw`, `analytics`, and `meta` schemas.
- Staging is replaced per run so stale rows cannot be accidentally reprocessed.
- Quarantine is retained by run so rejected records remain auditable.
- Deterministic `trip_id` plus a primary key and `ON CONFLICT DO NOTHING` makes curated loading repeat-safe.
- SQL quality gates prevent a run from being marked successful when core integrity rules fail.
- Analytics views provide a stable semantic layer for downstream BI.
- Airflow is an optional scheduling example, not a required local dependency.
