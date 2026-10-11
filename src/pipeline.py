import argparse
import uuid
from datetime import datetime, timezone

import pandas as pd
from sqlalchemy import text

from .extract import download_month, download_zone_lookup
from .load import ensure_metadata_schema, execute_sql_file, get_engine, load_dataframe
from .transform import transform_with_rejections


def _record_run(engine, values: dict) -> None:
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO meta.pipeline_runs
            (run_id, run_month, source_rows, accepted_rows, rejected_rows,
             status, error_message, started_at, finished_at)
            VALUES (:run_id, :run_month, :source_rows, :accepted_rows,
                    :rejected_rows, :status, :error_message,
                    :started_at, :finished_at)
        """), values)


def run(year: int, month: int, sample_rows: int | None = None):
    run_id = str(uuid.uuid4())
    run_month = f"{year}-{month:02d}"
    started_at = datetime.now(timezone.utc)
    source_rows = accepted_rows = rejected_rows = 0
    engine = get_engine()

    # Required database objects are created before any data work begins.
    ensure_metadata_schema()

    try:
        trip_path = download_month(year, month)
        zone_path = download_zone_lookup()
        source = pd.read_parquet(trip_path)
        if sample_rows:
            source = source.head(sample_rows)
        source_rows = len(source)

        result = transform_with_rejections(source)
        accepted = result.accepted.copy()
        rejected = result.rejected.copy()
        accepted_rows, rejected_rows = len(accepted), len(rejected)

        accepted["pipeline_run_id"] = run_id
        rejected["pipeline_run_id"] = run_id
        rejected["source_month"] = run_month

        # Staging is run-scoped: replace it so reruns cannot accidentally
        # reprocess rows left behind by an earlier execution.
        load_dataframe(accepted, "stg_yellow_trips", if_exists="replace")
        load_dataframe(rejected, "rejected_yellow_trips", if_exists="append")

        zones = pd.read_csv(zone_path)
        zones.columns = [c.lower() for c in zones.columns]
        zones.to_sql("taxi_zones", engine, schema="raw", if_exists="replace", index=False)

        # A run is not successful until warehouse loading, marts, and DQ checks pass.
        execute_sql_file("10_warehouse.sql")
        execute_sql_file("20_marts.sql")
        execute_sql_file("30_quality_checks.sql")

        finished_at = datetime.now(timezone.utc)
        _record_run(engine, {
            "run_id": run_id,
            "run_month": run_month,
            "source_rows": source_rows,
            "accepted_rows": accepted_rows,
            "rejected_rows": rejected_rows,
            "status": "success",
            "error_message": None,
            "started_at": started_at,
            "finished_at": finished_at,
        })
        print(
            f"Run {run_id}: loaded {accepted_rows:,}/{source_rows:,} accepted trips; "
            f"quarantined {rejected_rows:,}; warehouse and quality checks passed."
        )
    except Exception as exc:
        finished_at = datetime.now(timezone.utc)
        # Metadata schema was established before the try block, so failures are auditable.
        _record_run(engine, {
            "run_id": run_id,
            "run_month": run_month,
            "source_rows": source_rows,
            "accepted_rows": accepted_rows,
            "rejected_rows": rejected_rows,
            "status": "failed",
            "error_message": str(exc)[:1000],
            "started_at": started_at,
            "finished_at": finished_at,
        })
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load one month of NYC TLC Yellow Taxi data")
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--month", type=int, choices=range(1, 13), required=True)
    parser.add_argument("--sample-rows", type=int)
    args = parser.parse_args()
    run(args.year, args.month, args.sample_rows)
