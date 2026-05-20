import json
import math
import random
import time
from datetime import datetime, timezone

import paho.mqtt.client as mqtt

TOTAL_METERS = 1000
INTERVAL_SECONDS = 300  # 5 minutes

# MQTT settings
BROKER_HOST = "localhost"
BROKER_PORT = 1883
USERNAME = "admin"
PASSWORD = "Test@123"


def generate_power(hour):
  morning_peak = math.sin((hour - 7) / 24 * 2 * math.pi) * 2
  evening_peak = math.sin((hour - 19) / 24 * 2 * math.pi) * 4

  base = 2
  noise = random.uniform(-0.5, 0.5)

  power = base + morning_peak + evening_peak + noise

  return max(power, 0.2)


def on_connect(client, userdata, flags, rc, properties):
  if rc == 0:
    print(f"Connected successfully to MQTT Broker at {BROKER_HOST}:{BROKER_PORT}...")
  else:
    print(f"Failed to connect, return code {rc}\n")
    client.loop_stop()


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.username_pw_set(USERNAME, PASSWORD)
client.connect(BROKER_HOST, BROKER_PORT, 60)

client.loop_start()


try:
    while True:
      now = datetime.now(timezone.utc)
      hour = now.hour

      for i in range(TOTAL_METERS):
        meter_id = 1000000000 + i

        power = round(generate_power(hour), 2)
        voltage = round(random.uniform(220, 240), 2)
        current = round(power * 1000 / voltage, 2)
        frequency = round(random.uniform(49.8, 50.2), 2)
        energy = round(power * 0.0833, 4)

        payload = {
          'meter_id': meter_id,
          'timestamp': now.isoformat(),
          'power': power,
          'voltage': voltage,
          'current': current,
          'frequency': frequency,
          'energy': energy
        }

        topic = f'energy/meters/{meter_id}'

        client.publish(topic, json.dumps(payload))

      print(f'Published data for {TOTAL_METERS} meters')

      time.sleep(INTERVAL_SECONDS)
except KeyboardInterrupt:
  print("Program interrupted by user, exiting...")
finally:
  client.loop_stop()
  client.disconnect()
