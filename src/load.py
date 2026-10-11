from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text

from .config import BASE_DIR, DATABASE_URL


def get_engine():
    return create_engine(DATABASE_URL, pool_pre_ping=True)


def execute_sql_file(filename: str) -> None:
    sql = (Path(BASE_DIR) / "sql" / filename).read_text(encoding="utf-8")
    engine = get_engine()
    # psycopg2 accepts the project SQL scripts as multi-statement batches.
    with engine.begin() as conn:
        conn.exec_driver_sql(sql)


def ensure_metadata_schema() -> None:
    execute_sql_file("00_init.sql")


def load_dataframe(
    df: pd.DataFrame,
    table: str,
    schema: str = "raw",
    chunksize: int = 10_000,
    if_exists: str = "append",
) -> None:
    if df.empty:
        return
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema}"'))
    df.to_sql(
        table,
        engine,
        schema=schema,
        if_exists=if_exists,
        index=False,
        chunksize=chunksize,
        method="multi",
    )
