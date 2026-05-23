import time
import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port=5432,
    user='postgres',
    password='postgres',
    dbname='smart_grid'
)

cursor = conn.cursor()

queries = {
    'query_1': """
        SELECT time_bucket('1 hour', timestamp) AS hour, AVG(power) as avg_power
        FROM energy_readings_week
        WHERE timestamp >= DATE_TRUNC('day', NOW())
        GROUP BY hour
        ORDER BY hour;
    """,

    'query_2': """
        SELECT time_bucket('15 minutes', timestamp) AS period, AVG(power) as avg_power
        FROM energy_readings_week
        WHERE timestamp >= NOW() - INTERVAL '7 days'
        GROUP BY period
        ORDER BY avg_power DESC
        LIMIT 10;
    """,

    'query_3': """
        SELECT meter_id, DATE_TRUNC('month', timestamp) as month, SUM(energy) as total_energy
        FROM energy_readings_week
        GROUP BY meter_id, month
        ORDER BY month, total_energy DESC;
    """,

    'query_4': """
        SELECT COUNT(*), AVG(power), MAX(power), MIN(power)
        FROM energy_readings_week;
    """,
}

for name, query in queries.items():
    start = time.perf_counter()

    cursor.execute(query)
    cursor.fetchall()

    end = time.perf_counter()

    print(f'{name}: {end - start:.4f} seconds')

cursor.close()
conn.close()
