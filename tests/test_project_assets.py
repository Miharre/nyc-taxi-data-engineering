from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _sql(name: str) -> str:
    return (ROOT / "sql" / name).read_text(encoding="utf-8")


def test_init_sql_is_complete_and_creates_audit_table():
    sql = _sql("00_init.sql")
    assert "CREATE TABLE IF NOT EXISTS meta.pipeline_runs" in sql
    assert sql.strip().endswith(");")


def test_required_sql_stages_exist_and_are_nonempty():
    for name in ("10_warehouse.sql", "20_marts.sql", "30_quality_checks.sql"):
        path = ROOT / "sql" / name
        assert path.exists()
        assert path.stat().st_size > 100


def test_warehouse_load_is_idempotent():
    sql = _sql("10_warehouse.sql")
    assert "PRIMARY KEY" in sql
    assert "ON CONFLICT (trip_id) DO NOTHING" in sql


def test_expected_analytics_views_are_defined():
    sql = _sql("20_marts.sql")
    for view in ("v_daily_kpis", "v_zone_performance", "v_hourly_demand"):
        assert f"analytics.{view}" in sql


def test_quality_gate_checks_core_integrity_rules():
    sql = _sql("30_quality_checks.sql")
    assert "null trip_id" in sql
    assert "duplicate trip_id" in sql
    assert "invalid metrics" in sql
