# lidless-controller

Cloud-side microservice for the Lidless home monitoring system. Consumes sensor readings from RabbitMQ, persists to a write/read DB pair, and exposes a mould risk analysis API.

## Architecture
<img width="763" height="542" alt="overview" src="https://github.com/user-attachments/assets/137c6478-ea9b-4182-8968-6dcd23430f3f" />

- [OpsCheck](https://github.com/jimyeong/ops-check-service)
- [Lidless Oracle](https://github.com/jimyeong/lidless-oracle)(React Native Mobile Chatting App)
- [Lidless Hermes](https://github.com/jimyeong/lidless-hermes)(GraphQL Orchestration Server)
## Project Structure

```
lidless-controller/
├── app/
│   ├── main.py                  # FastAPI app and route definitions
│   └── physics.py               # Mould risk calculation (dew point model)
├── amqp_consumers/
│   └── raven_consumer.py        # RabbitMQ consumer — inserts readings into Write DB
└── core/
    └── db/
        ├── db.py                # WriteDB / ReadDB base classes
        ├── db_config.py         # DB config from environment variables
        ├── scheme.sql           # raven_reports table schema
        └── tests/
            └── test_db.py       # DB connection and replication tests
```

## API

### `GET /`
Health check.

```json
{ "message": "Lidless Controller AI is running" }
```

### `GET /api/analysis/mould-risk`

Returns a mould risk score for a given date range, based on a humidity/temperature CSV.

**Query Parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `from` | date | Yes | Start date (YYYY-MM-DD) |
| `to` | date | Yes | End date (YYYY-MM-DD) |

**Example**

```
GET /api/analysis/mould-risk?from=2026-05-01&to=2026-05-10
```

**Response**

```json
{
  "risk_score": 0.1234,
  "sample_count": 480,
  "status": "STABLE"
}
```

`status` is `STABLE` if `risk_score < 0.5`, otherwise `WARNING`.

## Mould Risk Model

Risk is calculated using the Magnus formula dew point approximation:

- **Dew point** is derived from temperature (°C) and relative humidity (%)
- A reading is flagged **at risk** when `temperature - dew_point < 3.0°C`
- **Risk score** = proportion of at-risk readings over the date range

## Data Source

The API reads from `humid_temp_readings.csv` in the project root by default. The CSV must include `received_at`, `temperature`, and `humidity` columns.

## RabbitMQ Consumer (Raven)

`raven_consumer.py` connects to a RabbitMQ broker and consumes messages from a configured queue, inserting payloads into the `raven_reports` table.

Dead-letter exchange (DLX) is configured — failed messages are routed to a DLQ instead of being requeued indefinitely.

**Environment Variables**

| Variable | Description |
|----------|-------------|
| `CLOUD_AMQP_URL` | RabbitMQ connection URL |
| `QUEUE_NAME` | Main queue to consume from |
| `DLX_EXCHANGE_NAME` | Dead-letter exchange name |
| `DLQ_NAME` | Dead-letter queue name |
| `ROUTING_KEY` | Routing key for DLX binding |

**Run the consumer**

```bash
python amqp_consumers/raven_consumer.py
```

## Database

Write DB and Read DB are separate — Write DB is the primary, Read DB is a replica.

**Environment Variables**

| Variable | Description |
|----------|-------------|
| `WRITE_DB_HOST` | Write DB host |
| `WRITE_DB_PORT` | Write DB port |
| `WRITE_DB_NAME` | Write DB name |
| `WRITE_DB_USER` | Write DB user |
| `WRITE_DB_PASSWORD` | Write DB password |
| `READ_DB_HOST` | Read DB host |
| `READ_DB_PORT` | Read DB port |
| `READ_DB_NAME` | Read DB name |
| `READ_DB_USER` | Read DB user |
| `READ_DB_PASSWORD` | Read DB password |

**Schema**

```sql
CREATE TABLE public.raven_reports (
    report_id serial NOT NULL,
    area TEXT NOT NULL,
    payload JSONB NOT NULL,
    created_at timestampWithTimeZone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT raven_reports_pk PRIMARY KEY (report_id)
);
```

**Test DB connections**

```bash
python core/db/tests/test_db.py
```

Tests write connection, read connection, and verifies the Read DB correctly rejects writes (replica check).

## Running the API

```bash
uvicorn app.main:app --reload
```

## Requirements

```
fastapi
uvicorn
pandas
pika
psycopg2
python-dotenv
```
