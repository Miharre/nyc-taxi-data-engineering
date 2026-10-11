CREATE OR REPLACE VIEW analytics.v_daily_kpis AS
SELECT pickup_datetime::date AS trip_date, COUNT(*) AS trips,
 ROUND(SUM(total_amount)::numeric,2) AS revenue,
 ROUND(AVG(trip_distance)::numeric,2) AS avg_distance_miles,
 ROUND(AVG(trip_duration_minutes)::numeric,2) AS avg_duration_minutes,
 ROUND(AVG(CASE WHEN fare_amount > 0 THEN tip_amount/fare_amount END)*100::numeric,2) AS avg_tip_pct
FROM analytics.fact_trips GROUP BY 1;

CREATE OR REPLACE VIEW analytics.v_zone_performance AS
SELECT l.borough, l.zone, COUNT(*) AS pickups,
 ROUND(SUM(f.total_amount)::numeric,2) AS revenue,
 ROUND(AVG(f.total_amount)::numeric,2) AS avg_ticket
FROM analytics.fact_trips f JOIN analytics.dim_location l ON l.location_id=f.pickup_location_id
GROUP BY 1,2;

CREATE OR REPLACE VIEW analytics.v_hourly_demand AS
SELECT pickup_day_of_week, pickup_hour, COUNT(*) AS trips,
 ROUND(AVG(total_amount)::numeric,2) AS avg_total_amount
FROM analytics.fact_trips GROUP BY 1,2;
