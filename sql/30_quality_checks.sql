DO $$ BEGIN
 IF EXISTS (SELECT 1 FROM analytics.fact_trips WHERE trip_id IS NULL) THEN RAISE EXCEPTION 'DQ: null trip_id'; END IF;
 IF EXISTS (SELECT trip_id FROM analytics.fact_trips GROUP BY trip_id HAVING COUNT(*)>1) THEN RAISE EXCEPTION 'DQ: duplicate trip_id'; END IF;
 IF EXISTS (SELECT 1 FROM analytics.fact_trips WHERE trip_distance<=0 OR trip_duration_minutes<=0 OR total_amount<0) THEN RAISE EXCEPTION 'DQ: invalid metrics'; END IF;
END $$;
