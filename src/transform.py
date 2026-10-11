import hashlib
from dataclasses import dataclass

import pandas as pd

RENAME = {
    "VendorID": "vendor_id",
    "RatecodeID": "rate_code_id",
    "PULocationID": "pickup_location_id",
    "DOLocationID": "dropoff_location_id",
    "Airport_fee": "airport_fee",
}

REQUIRED = [
    "pickup_datetime", "dropoff_datetime", "pickup_location_id",
    "dropoff_location_id", "trip_distance", "fare_amount", "total_amount",
]


@dataclass(frozen=True)
class TransformResult:
    accepted: pd.DataFrame
    rejected: pd.DataFrame


def _trip_id(row: pd.Series) -> str:
    """Build a reproducible trip key from fields that identify the observed trip."""
    parts = [
        row.get("pickup_datetime"), row.get("dropoff_datetime"),
        row.get("pickup_location_id"), row.get("dropoff_location_id"),
        row.get("trip_distance"), row.get("total_amount"), row.get("vendor_id"),
    ]
    payload = "|".join("<null>" if pd.isna(v) else str(v) for v in parts)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def transform_with_rejections(df: pd.DataFrame) -> TransformResult:
    work = df.rename(columns=RENAME).copy()
    work.columns = [c.lower() for c in work.columns]
    work["pickup_datetime"] = pd.to_datetime(work.pop("tpep_pickup_datetime"), errors="coerce")
    work["dropoff_datetime"] = pd.to_datetime(work.pop("tpep_dropoff_datetime"), errors="coerce")
    work["trip_duration_minutes"] = (
        work["dropoff_datetime"] - work["pickup_datetime"]
    ).dt.total_seconds() / 60

    reasons = pd.Series("", index=work.index, dtype="object")

    def reject(mask: pd.Series, reason: str) -> None:
        nonlocal reasons
        mask = mask.fillna(True)
        reasons.loc[mask & reasons.eq("")] = reason

    reject(work[[c for c in REQUIRED if c in work.columns]].isna().any(axis=1), "missing_required_field")
    reject(work["trip_distance"].le(0) | work["trip_distance"].gt(100), "invalid_trip_distance")
    reject(work["trip_duration_minutes"].le(0) | work["trip_duration_minutes"].gt(360), "invalid_trip_duration")
    reject(work["fare_amount"].lt(0) | work["total_amount"].lt(0), "negative_financial_amount")
    reject(
        ~work["pickup_location_id"].between(1, 265) | ~work["dropoff_location_id"].between(1, 265),
        "invalid_taxi_zone",
    )

    rejected = work.loc[reasons.ne("")].copy()
    rejected["rejection_reason"] = reasons.loc[rejected.index]

    accepted = work.loc[reasons.eq("")].copy()
    accepted["pickup_date"] = accepted["pickup_datetime"].dt.date
    accepted["pickup_hour"] = accepted["pickup_datetime"].dt.hour
    accepted["pickup_year"] = accepted["pickup_datetime"].dt.year
    accepted["pickup_month"] = accepted["pickup_datetime"].dt.month
    accepted["pickup_day_of_week"] = accepted["pickup_datetime"].dt.day_name()
    accepted["trip_id"] = accepted.apply(_trip_id, axis=1)
    accepted = accepted.drop_duplicates("trip_id")

    return TransformResult(accepted=accepted, rejected=rejected)


def transform_trips(df: pd.DataFrame) -> pd.DataFrame:
    """Compatibility wrapper used by simple callers and unit tests."""
    return transform_with_rejections(df).accepted
