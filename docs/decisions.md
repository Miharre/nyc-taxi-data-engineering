# Engineering decisions

## 1. PostgreSQL instead of a cloud warehouse

For a portfolio repository, reproducibility matters. A reviewer should be able to run the core system without creating a paid cloud account. PostgreSQL provides real schemas, constraints, indexes, transactions, and SQL modeling while keeping the environment small.

## 2. Quarantine invalid rows instead of deleting them

Filtering invalid rows would erase evidence about what was rejected. The project retains rejected rows with a reason, source month, and pipeline run ID.

## 3. Curated idempotency and quarantine history serve different goals

The curated fact table should not duplicate a trip when the same source is rerun. Quarantine is run-level operational evidence, so rejected rows are retained per execution.

## 4. Deterministic SHA-256 trip key

The source does not provide one identifier suitable for repeat-safe loading. I derive one from pickup/drop-off timestamps, pickup/drop-off locations, distance, total amount, and vendor. This is an explicit project deduplication rule, not a claim of a universally perfect natural key.

## 5. SQL views instead of dashboard-specific transformations

KPI definitions live in SQL so a dashboard is not the only place where business logic exists. The same views can be inspected directly and consumed by different BI tools.

## 6. Batch orchestration

TLC data arrives as monthly files, so batch matches the source. Streaming infrastructure would increase complexity without solving a source-latency requirement.

## 7. Airflow remains optional

The DAG demonstrates how the same pipeline entry point can be scheduled. The laptop quick start does not require Airflow and the repository does not claim a hosted Airflow deployment.
