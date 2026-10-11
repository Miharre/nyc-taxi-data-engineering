CREATE TABLE IF NOT EXISTS analytics.dim_location (
  location_id INT PRIMARY KEY,
  borough TEXT,
  zone TEXT,
  service_zone TEXT
);

CREATE TABLE IF NOT EXISTS analytics.fact_trips (
  trip_id TEXT PRIMARY KEY,
  pickup_datetime TIMESTAMP NOT NULL,
  dropoff_datetime TIMESTAMP NOT NULL,
  pickup_location_id INT NOT NULL,
  dropoff_location_id INT NOT NULL,
  passenger_count NUMERIC,
  trip_distance NUMERIC NOT NULL,
  fare_amount NUMERIC NOT NULL,
  tip_amount NUMERIC,
  tolls_amount NUMERIC,
  total_amount NUMERIC NOT NULL,
  payment_type INT,
  trip_duration_minutes NUMERIC NOT NULL,
  pickup_hour INT NOT NULL,
  pickup_year INT NOT NULL,
  pickup_month INT NOT NULL,
  pickup_day_of_week TEXT NOT NULL,
  cbd_congestion_fee NUMERIC DEFAULT 0,
  pipeline_run_id UUID NOT NULL
);

TRUNCATE analytics.dim_location;
INSERT INTO analytics.dim_location(location_id, borough, zone, service_zone)
SELECT locationid::int, borough, zone, service_zone
FROM raw.taxi_zones;

INSERT INTO analytics.fact_trips (
  trip_id, pickup_datetime, dropoff_datetime, pickup_location_id, dropoff_location_id,
  passenger_count, trip_distance, fare_amount, tip_amount, tolls_amount, total_amount,
  payment_type, trip_duration_minutes, pickup_hour, pickup_year, pickup_month,
  pickup_day_of_week, cbd_congestion_fee, pipeline_run_id
)
SELECT
  trip_id, pickup_datetime, dropoff_datetime, pickup_location_id::int, dropoff_location_id::int,
  passenger_count, trip_distance, fare_amount, tip_amount, tolls_amount, total_amount,
  payment_type::int, trip_duration_minutes, pickup_hour::int, pickup_year::int,
  pickup_month::int, pickup_day_of_week, COALESCE(cbd_congestion_fee, 0), pipeline_run_id::uuid
FROM raw.stg_yellow_trips
ON CONFLICT (trip_id) DO NOTHING;

CREATE INDEX IF NOT EXISTS idx_fact_pickup_datetime ON analytics.fact_trips(pickup_datetime);
CREATE INDEX IF NOT EXISTS idx_fact_pickup_location ON analytics.fact_trips(pickup_location_id);
