import pandas as pd
from src.transform import transform_trips, transform_with_rejections


def row(distance=2.5, total=20.0, pickup="2026-01-01 10:00:00"):
    return {"VendorID": 2, "tpep_pickup_datetime": pickup,
            "tpep_dropoff_datetime": "2026-01-01 10:15:00",
            "PULocationID": 161, "DOLocationID": 236, "passenger_count": 1,
            "trip_distance": distance, "fare_amount": 15.0, "tip_amount": 3.0,
            "tolls_amount": 0.0, "total_amount": total, "payment_type": 1}


def test_transform_adds_engineered_fields():
    out = transform_trips(pd.DataFrame([row()]))
    assert len(out) == 1
    assert out.iloc[0].trip_duration_minutes == 15
    assert out.iloc[0].pickup_hour == 10
    assert len(out.iloc[0].trip_id) == 64


def test_invalid_distance_is_quarantined_with_reason():
    result = transform_with_rejections(pd.DataFrame([row(distance=-1)]))
    assert result.accepted.empty
    assert result.rejected.iloc[0].rejection_reason == "invalid_trip_distance"


def test_missing_timestamp_is_quarantined():
    result = transform_with_rejections(pd.DataFrame([row(pickup=None)]))
    assert result.accepted.empty
    assert result.rejected.iloc[0].rejection_reason == "missing_required_field"


def test_deduplicates_deterministically():
    r = row()
    out = transform_trips(pd.DataFrame([r, r]))
    assert len(out) == 1
    assert out.iloc[0].trip_id == transform_trips(pd.DataFrame([r])).iloc[0].trip_id


def test_valid_and_invalid_rows_are_accounted_for():
    result = transform_with_rejections(pd.DataFrame([row(), row(distance=0)]))
    assert len(result.accepted) + len(result.rejected) == 2
