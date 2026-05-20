SELECT create_hypertable(
  'energy_readings',
  'timestamp',
  chunk_time_interval => INTERVAL '1 day'
);

CREATE TABLE energy_readings_3h (
  LIKE energy_readings INCLUDING ALL
);

CREATE TABLE energy_readings_week (
  LIKE energy_readings INCLUDING ALL
);

SELECT create_hypertable(
  'energy_readings_3h',
  'timestamp',
  chunk_time_interval => INTERVAL '3 hours'
);

SELECT create_hypertable(
  'energy_readings_week',
  'timestamp',
  chunk_time_interval => INTERVAL '1 week'
);
