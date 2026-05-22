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


import random

def generate_power(hour, meter_bias = 1.0):
  """Generate realistic smart-meter power usage patterns."""
  
  base = random.uniform(0.3, 1.2)
  peak = 0.2

  if 6.0 <= hour < 9.0:
    # Morning peak (06:00 to 08:59)
    peak = random.uniform(2.0, 5.0)
  elif 9.0 <= hour < 17.0:
     # Daytime moderate usage (09:00 to 16:59)
    peak = random.uniform(1.0, 3.0)
  elif 17.0 <= hour < 22.0:
    # Evening peak (17:00 to 21:59)
    peak = random.uniform(4.0, 8.0)
  else:
    # Night low usage (22:00 to 05:59)
    peak = random.uniform(0.2, 1.0)

  appliance_spike = random.choice([0.0, 0.0, 0.0, random.uniform(1.0, 3.0)])
  noise = random.uniform(-0.3, 0.3)

  total_power = (base + peak + appliance_spike) * meter_bias + noise

  return round(max(total_power, 0.2), 2)


start_date = datetime.now(timezone.utc) - timedelta(weeks=4)
end_date = datetime.now(timezone.utc)

current = start_date
buffer = []

while current < end_date:
  hour = current.hour + (current.minute / 60.0)

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
