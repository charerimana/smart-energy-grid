import math
import random
from datetime import datetime, timedelta, timezone

import psycopg2
from psycopg2.extras import execute_values

TOTAL_METERS = 1000
BATCH_SIZE = 10000

conn = psycopg2.connect(
  host='localhost',
  port=5432,
  user='postgres',
  password='postgres',
  dbname='smart_grid'
)

cursor = conn.cursor()


def generate_power(hour):
  morning_peak = math.sin((hour - 7) / 24 * 2 * math.pi) * 2
  evening_peak = math.sin((hour - 19) / 24 * 2 * math.pi) * 4

  base = 2
  noise = random.uniform(-0.5, 0.5)

  return max(base + morning_peak + evening_peak + noise, 0.2)


start_date = datetime.now(timezone.utc) - timedelta(weeks=4)
end_date = datetime.now(timezone.utc)

current = start_date
buffer = []

while current < end_date:
  hour = current.hour

  for i in range(TOTAL_METERS):
    meter_id = 1000000000 + i

    power = round(generate_power(hour), 2)
    voltage = round(random.uniform(220, 240), 2)
    current_amp = round(power * 1000 / voltage, 2)
    frequency = round(random.uniform(49.8, 50.2), 2)
    energy = round(power * 0.0833, 4)

    row = (
      meter_id,
      current,
      power,
      voltage,
      current_amp,
      frequency,
      energy
    )

    buffer.append(row)

    if len(buffer) >= BATCH_SIZE:
      execute_values(
        cursor,
        """
        INSERT INTO energy_readings (
            meter_id,
            timestamp,
            power,
            voltage,
            current,
            frequency,
            energy
        ) VALUES %s
        """,
        buffer
      )

      conn.commit()

      print(f'Inserted {len(buffer)} rows')

      buffer = []

  current += timedelta(minutes=5)

# Catch any trailing rows left over at the end
if buffer:
    execute_values(
      cursor,
      """
      INSERT INTO energy_readings (
        meter_id,
        timestamp,
        power,
        voltage,
        current,
        frequency,
        energy
      ) VALUES %s
      """,
      buffer
    )

    conn.commit()

cursor.close()
conn.close()

print('Historical data generation complete')
