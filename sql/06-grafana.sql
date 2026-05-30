-- Query 1: Real-Time Meter Readings
SELECT
  timestamp AS time,
  -- time_bucket('1 hour', timestamp) AS time,
  AVG(power) AS "Current Average Load (kW)",
  MAX(power) AS "Max Peak (kW)"
FROM
  energy_readings
WHERE
  -- timestamp >= NOW() - INTERVAL '1 hour'
  $__timeFilter(timestamp)
GROUP BY
  timestamp
ORDER BY
  timestamp ASC;


-- Query 2: Daily Consumption Patterns
SELECT
  time_bucket('1 hour', timestamp) AS time,
  CASE
    WHEN DATE(timestamp) = CURRENT_DATE THEN 'Today'
    ELSE 'Yesterday'
  END AS day_type,
  AVG(power) AS avg_power
FROM energy_readings
WHERE DATE(timestamp) IN (
  CURRENT_DATE,
  CURRENT_DATE - INTERVAL '1 day'
)
GROUP BY time, day_type
ORDER BY time;


-- Query 3: Weekly Trends
SELECT
  time_bucket('7 day', timestamp) AS time,
  AVG(power) AS avg_power
FROM
  energy_readings -- WHERE timestamp >= NOW() - INTERVAL '7 days'
WHERE
  $__timeFilter(timestamp)
GROUP BY
  time
ORDER BY
  time;


-- Query 4: Monthly Energy Usage by Region
SELECT
  CASE RIGHT(meter_id::text, 1)
    WHEN '0' THEN 'Zone 0'
    WHEN '1' THEN 'Zone 1'
    WHEN '2' THEN 'Zone 2'
    WHEN '3' THEN 'Zone 3'
    WHEN '4' THEN 'Zone 4'
    WHEN '5' THEN 'Zone 5'
    WHEN '6' THEN 'Zone 6'
    WHEN '7' THEN 'Zone 7'
    WHEN '8' THEN 'Zone 8'
    WHEN '9' THEN 'Zone 9'
  END AS metric,
  SUM(energy) AS "Total Regional Usage (kWh)"
FROM energy_readings
WHERE $__timeFilter(timestamp)
GROUP BY metric
ORDER BY "Total Regional Usage (kWh)" DESC;


-- Query 5: Query Execution Time Comparison
SELECT
  *
FROM
  (
    VALUES
      ('Raw Query', 0.863),
      ('Continuous Aggregate', 0.332)
  ) AS t(series, execution_time_ms);


-- Query 6: Compression Storage Comparison
SELECT * FROM (
  VALUES
    ('energy_readings', 'Before Compression', 1004),
    ('energy_readings', 'After Compression', 356),

    ('energy_readings_3h', 'Before Compression', 1075),
    ('energy_readings_3h', 'After Compression', 373),

    ('energy_readings_week', 'Before Compression', 1041),
    ('energy_readings_week', 'After Compression', 382)
) AS t(hypertable, stage, storage_mb);


-- Query 7: Continuous Aggregates
SELECT * FROM (
  VALUES
    ('Raw Data - 1 Day Chunk', 0.863),
    ('Raw Data - 3 Hour Chunk', 2.820),
    ('Raw Data - Weekly Chunk', 0.750),

    ('Continuous Aggregate - 15min', 0.332),
    ('Continuous Aggregate - Hourly', 0.091),
    ('Continuous Aggregate - Daily', 0.055)
) AS t(metric, execution_time_ms);
