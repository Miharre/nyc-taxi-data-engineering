# Data contract and validation policy

The source is the NYC TLC Yellow Taxi monthly Parquet feed. This project does not assume that a public dataset is clean simply because it is published by an official source.

## Fields used as pipeline inputs
The transformation expects pickup/drop-off timestamps, pickup/drop-off location IDs, trip distance, fare amount, and total amount. Other source fields are preserved when available and selected measures are promoted into the warehouse fact table.

## Quarantine rules
A row is excluded from the analytical fact table and written to `raw.rejected_yellow_trips` with a reason when it has a missing required field, a nonpositive or >100-mile distance, a nonpositive or >6-hour duration, a negative fare/total, or a location ID outside 1–265.

These limits are engineering guardrails, not claims about TLC policy. They are deliberately visible here so they can be reviewed and changed instead of being buried in code.

## Duplicate policy
For accepted rows, the pipeline creates a SHA-256 key from pickup/drop-off time, pickup/drop-off location, distance, total amount, and vendor. Exact business-key collisions are treated as duplicate observations. The warehouse primary key and `ON CONFLICT DO NOTHING` make repeat loads safe at the curated layer.

## Auditability
Every accepted and rejected staging row receives a `pipeline_run_id`. `meta.pipeline_runs` records source, accepted, and rejected counts plus start/end timestamps and failure text when applicable.
