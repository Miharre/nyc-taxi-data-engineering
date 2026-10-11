# Validation evidence

This document records measured results from local Docker validation against the project warehouse. It separates observed evidence from architectural claims.

## Environment

- Pipeline runtime: Python 3.11 container
- Warehouse: PostgreSQL 16 container
- Demonstration input: first 100,000 rows of January 2026 Yellow Taxi data
- Method: two repeated pipeline executions against the same PostgreSQL volume, followed by SQL checks and Pytest

## End-to-end run evidence

| Metric | Run 1 | Run 2 |
| --- | ---: | ---: |
| Source rows | 100,000 | 100,000 |
| Accepted rows | 94,728 | 94,728 |
| Rejected rows | 5,272 | 5,272 |
| Status | success | success |

Pipeline logs reported that warehouse loading and quality checks passed for both runs.

## Idempotency

After both runs, the fact table contained 94,728 rows, 94,728 unique trip IDs, and 0 duplicate rows. The second run did not double the curated fact table.

## Quarantine lineage

The quarantine table retained 5,272 rejected observations for each pipeline run. Across the two runs, 10,544 quarantine observations were stored:

| Rejection reason | Observations across two runs |
| --- | ---: |
| `negative_financial_amount` | 3,672 |
| `invalid_trip_distance` | 3,612 |
| `invalid_trip_duration` | 3,260 |
| **Total** | **10,544** |

A rejection row has `pipeline_run_id` and `source_month`, allowing it to be traced to an execution.

## Warehouse integrity

The validated warehouse contained 94,728 fact rows, 265 location rows, zero duplicate trip IDs, zero nonpositive trip distances, zero nonpositive trip durations, and zero negative total amounts.

The daily KPI view reconciled exactly to the fact table:

| Trip date | Trips | Revenue |
| --- | ---: | ---: |
| 2025-12-31 | 5 | $329.85 |
| 2026-01-01 | 63,149 | $1,928,161.96 |
| 2026-01-02 | 31,574 | $926,501.99 |
| **Total trips** | **94,728** | |

The five 2025-12-31 rows are retained rather than hidden; they are boundary timestamps present in the bounded source sample.

## Analytics evidence

The three BI-facing views were present and queryable: `analytics.v_daily_kpis`, `analytics.v_hourly_demand`, and `analytics.v_zone_performance`.

For this sample, the highest-volume pickup zone was JFK Airport with 7,116 pickups and $537,475.72 in revenue. The highest-volume day/hour combination was Friday at 13:00 with 5,146 trips.

## Automated tests

The validated run collected seven tests and all seven passed. The final repository also strengthens static SQL asset coverage; run the current suite to see its current test count.

## Reproduce the checks

```bash
docker compose up -d --build
docker compose logs pipeline
docker compose run --rm pipeline pytest -v
make verify
```
