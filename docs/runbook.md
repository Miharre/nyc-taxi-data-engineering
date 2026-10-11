# Operator runbook

## Normal local run

```bash
docker compose up -d --build
docker compose logs pipeline
```

The default container command runs the bounded 100,000-row demonstration and executes warehouse loading, analytics views, and database quality checks in the same pipeline.

Run tests:

```bash
docker compose run --rm pipeline pytest -v
```

Verify recent audit records and the curated fact count:

```bash
make verify
```

## Run a selected month

```bash
docker compose run --rm pipeline python -m src.pipeline --year 2026 --month 1
```

Add `--sample-rows 100000` for a bounded demonstration.

## Checks after a load

1. Confirm the latest `meta.pipeline_runs.status` is `success`.
2. Reconcile `source_rows = accepted_rows + rejected_rows`.
3. Review rejection rate and reasons.
4. Confirm the fact table contains no duplicate `trip_id`.
5. Query the analytics views and confirm expected coverage.

## Failure handling

Failures after metadata initialization are recorded in `meta.pipeline_runs` with error text and the process exits non-zero. Fix the source, schema, network, or database issue and rerun the same month.

## Inspect quarantine lineage

```sql
SELECT pipeline_run_id, rejection_reason, COUNT(*) AS rows
FROM raw.rejected_yellow_trips
GROUP BY pipeline_run_id, rejection_reason
ORDER BY pipeline_run_id, rows DESC;
```

## Reset the local environment

```bash
docker compose down -v --remove-orphans
```

This deletes the local PostgreSQL volume and warehouse history. Use it only when a clean rebuild is intentional.
