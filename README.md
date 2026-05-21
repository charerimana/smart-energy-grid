# Smart Energy Grid Monitoring System

A smart energy monitoring and analytics platform built using:

- TimescaleDB
- PostgreSQL
- EMQX MQTT Broker
- Grafana
- Python
- Docker
- uv

The project simulates smart meter readings for 1000+ meters, stores time-series data in TimescaleDB, performs performance benchmarking, and visualizes analytics using Grafana dashboards.

---

# Features

- MQTT-based smart meter data ingestion
- Real-time energy monitoring
- TimescaleDB hypertables
- Compression benchmarking
- Continuous aggregations
- Grafana dashboards
- Historical data simulation
- Query performance analysis

---

# Project Structure

```text
smart-energy-grid/
│
├── docker-compose.yml
├── pyproject.toml
├── uv.lock
├── README.md
│
├── sql/
│   ├── schema.sql
│   ├── hypertables.sql
│   ├── compression.sql
│   ├── continuous_aggregates.sql
│   └── benchmark_queries.sql
│
├── simulator/
│   ├── generator.py
│   └── historical_loader.py
│
├── ingestion/
│   └── subscriber.py
│
├── benchmark/
│   └── benchmark.py
│
├── dashboard/
│
└── report/
```

---

# Technologies Used

| Technology | Purpose |
|---|---|
| TimescaleDB | Time-series database |
| PostgreSQL | Database engine |
| EMQX | MQTT broker |
| Grafana | Dashboard visualization |
| Python | Data generation and ingestion |
| Docker | Infrastructure containerization |
| uv | Python package management |

---

# Requirements

Install:

- Docker
- Docker Compose
- Python 3.11+
- uv

Install uv:

## Linux/macOS

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Windows

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

---

# Setup Instructions

# 1. Clone Repository

```bash
git clone git@github.com:charerimana/smart-energy-grid.git
cd smart-energy-grid
```

---

# 2. Install Python Dependencies

```bash
uv sync
```

Or manually add dependencies:

```bash
uv add paho-mqtt psycopg2-binary numpy
```

---

# 3. Start Infrastructure Services

Start:

- TimescaleDB
- EMQX
- Grafana

```bash
docker compose up -d
```

Check running containers:

```bash
docker compose ps
```

---

# 4. Access Services

## EMQX Dashboard

URL:

```text
http://localhost:18083
```

Default credentials:

```text
username: admin
password: public
```

---

## Grafana Dashboard

URL:

```text
http://localhost:3000
```

Default credentials:

```text
username: admin
password: admin
```

---

# 5. Run SQL Schema

Connect to PostgreSQL:

```bash
docker compose exec timescaledb psql -U postgres -d smart_grid
```

Run schema manually:

```sql
CREATE EXTENSION IF NOT EXISTS timescaledb;

CREATE TABLE IF NOT EXISTS energy_readings (
    meter_id BIGINT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    power DOUBLE PRECISION,
    voltage DOUBLE PRECISION,
    current DOUBLE PRECISION,
    frequency DOUBLE PRECISION,
    energy DOUBLE PRECISION,

    PRIMARY KEY (meter_id, timestamp)
);
```

Exit PostgreSQL:

```text
\q
```

---

# Running SQL Files

SQL files can be executed directly from the host machine without manually entering the PostgreSQL shell.

Example:

```bash
docker compose exec -T timescaledb \
psql -U postgres -d smart_grid -f - < sql/02-hypertables.sql
```

---

## Important Notes

- Ensure containers are running before executing SQL files:
- Ensure SQL files exist in the `sql/` directory.
- Run schema creation before hypertable creation.
- Run hypertable creation before inserting large datasets.

# 6. Create Hypertable

Run:

```sql
SELECT create_hypertable(
    'energy_readings',
    'timestamp',
    chunk_time_interval => INTERVAL '1 day'
);
```

Verify:

```sql
SELECT * FROM timescaledb_information.hypertables;
```

---

# Running the Project

# 1. Run MQTT Subscriber

The subscriber listens for MQTT messages and stores them into TimescaleDB.

```bash
uv run python ingestion/subscriber.py
```

---

# 2. Run Real-Time Generator

The generator simulates smart meter data and publishes it to MQTT.

```bash
uv run python simulator/generator.py
```

---

# 3. Generate Historical Data

Generate approximately 4 weeks of historical data.

```bash
uv run python simulator/historical_loader.py
```

---

# 4. Run Benchmarks

```bash
uv run python benchmark/benchmark.py
```

---

# Useful Docker Commands

# Start Services

```bash
docker compose up -d
```

---

# Stop Services

```bash
docker compose down
```

---

# Restart Services

```bash
docker compose restart
```

---

# View Running Containers

```bash
docker compose ps
```

---

# View Logs

## TimescaleDB

```bash
docker compose logs -f timescaledb
```

## EMQX

```bash
docker compose logs -f emqx
```

## Grafana

```bash
docker compose logs -f grafana
```

---

# Database Persistence

Docker volumes are used to persist:

- PostgreSQL data
- Grafana dashboards
- EMQX configuration

Important:

```bash
docker compose down
```

preserves data.

However:

```bash
docker compose down -v
```

removes all persistent volumes and deletes stored data.

---

# Dashboard Requirements

The Grafana dashboard should include:

- Real-time meter readings
- Daily consumption patterns
- Weekly trends
- Monthly usage by region
- Compression metrics
- Query performance comparisons

---

# Benchmarking Notes

Before running benchmarks:

Restart PostgreSQL to simulate cold-cache conditions.

```bash
docker compose restart timescaledb
```

---

# MQTT Configuration

The project uses EMQX as the MQTT broker.

Default broker configuration used in the Python scripts:

```python
BROKER_HOST = "localhost"
BROKER_PORT = 1883
USERNAME = "admin"
PASSWORD = "Test@123"
```

- Ensure the authentication user is created before running Python scripts.
- Update credentials in the Python scripts if different credentials are used.
- Ensure EMQX authentication is enabled if testing secured MQTT access.

---

# MQTT Topic Structure

```text
energy/meters/{meter_id}
```

Example:

```text
energy/meters/1000000001
```

---

# Example MQTT Payload

```json
{
  "meter_id": 1000000001,
  "timestamp": "2026-05-20T10:00:00Z",
  "power": 2.5,
  "voltage": 230,
  "current": 10.8,
  "frequency": 50.0,
  "energy": 1.2
}
```

---

# Expected Dataset Size

Approximate dataset:

- 1000 meters
- 5-minute intervals
- 4 weeks
- ~8 million rows

---

# Important Notes

- Use UTC timestamps
- Avoid inserting rows one-by-one
- Use batch inserts
- Restart PostgreSQL before benchmark tests
- Save Grafana dashboards manually

---

# Possible Improvements

The current implementation provides the core functionality required for the project. However, several improvements can be made to enhance scalability, maintainability, performance, and production readiness.

## 1. Reduce Code Repetition

Some logic is repeated across:
- `generator.py`
- `historical_loader.py`

---

## 2. Add Environment Variable Support

Currently, database and MQTT configurations are hardcoded.

---

## 3. Add Logging System

The project currently uses simple `print()` statements.

This can be improved using Python’s `logging` module.

---

## 4. Add Error Handling and Retry Logic

The system can be improved by handling:
- MQTT disconnections
- database connection failures
- malformed payloads
- network interruptions

Retry mechanisms and reconnection logic would improve reliability.

---

## 5. Add Data Validation

Incoming MQTT payloads are currently assumed to be valid.

Validation can be added to ensure:
- required fields exist
- numeric fields are valid
- timestamps are correctly formatted

This improves robustness and prevents invalid database entries.

---

## 6. Improve Dashboard Design

Current dashboards can be enhanced with:
- alert panels
- anomaly detection indicators
- dynamic meter selection
- live refresh optimization

---

## 7. Add Automated Benchmark Reporting

Benchmark results are currently printed manually.

This can be improved by:
- exporting results to CSV
- generating charts automatically
- storing benchmark history

---

## 8. Add Docker Health Checks

Health checks can improve service reliability.

---

## 9. Optimize Database Performance Further

Additional optimization opportunities include:
- advanced indexing strategies
- retention policies
- data downsampling
- partition tuning
- query optimization using execution plans

---

## 10. Improve Security

The current setup is designed for development purposes.

---

## 11. Add Real Smart Meter Integration

Currently, all data is simulated.

In future, add real IoT devices could be integrated.

---

## 12. Add Machine Learning Analytics

Future enhancements may include:
- anomaly detection
- energy consumption forecasting
- predictive maintenance
- usage pattern classification

This would provide more advanced analytics capabilities.

# Contributors

- Ernest NDACYAYISENGA
- Kevin RUBERWA
- Carlos HARERIMANA
