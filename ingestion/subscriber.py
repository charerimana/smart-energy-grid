import json
import psycopg2
from psycopg2.extras import execute_values
import paho.mqtt.client as mqtt

# MQTT settings
BROKER_HOST = "localhost"
BROKER_PORT = 1883
USERNAME = "admin"
PASSWORD = "Test@123"

BATCH_SIZE = 2000
buffer = []

conn = psycopg2.connect(
  host='localhost',
  port=5432,
  user='postgres',
  password='postgres',
  dbname='smart_grid'
)

cursor = conn.cursor()

def flush_buffer():
  global buffer

  if not buffer:
    return

  query = """
      INSERT INTO energy_readings (
        meter_id,
        timestamp,
        power,
        voltage,
        current,
        frequency,
        energy
      ) VALUES %s
  """

  try:
    execute_values(cursor, query, buffer)
    conn.commit()

    print(f'Inserted {len(buffer)} rows')
  except Exception as e:
    conn.rollback()
    print(f"Error during execution context flush: {e}")
  finally:
    buffer = []


def on_connect(client, userdata, flags, rc, properties):
  if rc == 0:
    print(f"Connected successfully to MQTT Broker at {BROKER_HOST}:{BROKER_PORT}...")
    client.subscribe('energy/meters/#')
  else:
    print(f"Failed to connect, return code {rc}\n")


def on_message(client, userdata, msg):
  global buffer

  data = json.loads(msg.payload.decode())

  row = (
    int(data['meter_id']),
    data['timestamp'],
    float(data['power']),
    float(data['voltage']),
    float(data['current']),
    float(data['frequency']),
    float(data['energy'])
  )

  buffer.append(row)

  if len(buffer) >= BATCH_SIZE:
    flush_buffer()


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set(USERNAME, PASSWORD)
client.connect(BROKER_HOST, BROKER_PORT, 60)

try:
  client.loop_forever()
except KeyboardInterrupt:
  print("\nShutting down consumer pipeline gracefully...")
finally:
  flush_buffer()
  cursor.close()
  conn.close()
