# Interview guide

## 30-second explanation

I built a batch data pipeline around NYC TLC Yellow Taxi records. Python downloads monthly Parquet data, validates it, separates bad records into a reason-coded quarantine table, and loads accepted records into PostgreSQL. SQL builds a fact table, location dimension, quality gates, and three analytics views. Docker makes the project reproducible, Pytest covers transformation behavior, GitHub Actions defines CI, and an optional Airflow DAG shows how I would schedule the same pipeline entry point.

## What did you verify?

In my bounded validation run, each execution processed 100,000 source rows: 94,728 were accepted and 5,272 were quarantined. I ran the same input twice and the fact table stayed at 94,728 unique trips with zero duplicate trip IDs. Quarantine kept a separate 5,272-row batch for each run so rejected records remained traceable.

## Why PostgreSQL?

It lets a reviewer run the core project without a cloud account while still demonstrating schemas, constraints, indexes, transactions, dimensional modeling, audit metadata, and SQL analytics.

## Why batch instead of streaming?

The upstream source is monthly. Streaming would add infrastructure without reducing source latency.

## How is it idempotent?

I derive a deterministic SHA-256 key from selected trip attributes, deduplicate accepted rows on that key, and make it the fact-table primary key. The warehouse inserts with `ON CONFLICT DO NOTHING`.

## How do you handle bad data?

Invalid records go to `raw.rejected_yellow_trips` with a reason, `pipeline_run_id`, and source month. SQL quality gates provide a second layer of protection before a run is recorded as successful.

## What would you improve for production?

Immutable object storage, secrets management, schema/freshness observability, historical anomaly thresholds, stronger database integration tests, managed orchestration, partitioned analytical storage, and SLA-based alerting.

## Resume bullets

- Built a Dockerized batch data pipeline using Python, SQL, and PostgreSQL to transform NYC TLC Parquet data into an auditable analytical warehouse.
- Implemented reason-coded quarantine, deterministic deduplication, repeat-safe fact loading, run-level lineage, and SQL data-quality gates.
- Created dimensional models and BI-facing views for daily KPIs, hourly demand, and taxi-zone performance; validated a 100,000-row sample with zero duplicate curated facts.
