# lidless-controller

A lightweight Python microservice that exposes a mould risk analysis API and includes a RabbitMQ consumer for ingesting sensor readings.

## Overview

lidless-controller sits alongside the Opscheck stack. It reads humidity/temperature data and calculates mould risk scores using a dew point model, exposed via a REST API.

## Project Structure

```
lidless-controller/
├── app/
│   ├── main.py        # FastAPI app and route definitions
│   └── physics.py     # Mould risk calculation (dew point model)
└── amqp_consumers/
    └── raven_consumer.py  # RabbitMQ consumer — inserts readings into DB
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

| Parameter | Type   | Required | Description        |
|-----------|--------|----------|--------------------|
| `from`    | date   | Yes      | Start date (YYYY-MM-DD) |
| `to`      | date   | Yes      | End date (YYYY-MM-DD)   |

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

| Variable            | Description                        |
|---------------------|------------------------------------|
| `CLOUD_AMQP_URL`    | RabbitMQ connection URL            |
| `QUEUE_NAME`        | Main queue to consume from         |
| `DLX_EXCHANGE_NAME` | Dead-letter exchange name          |
| `DLQ_NAME`          | Dead-letter queue name             |
| `ROUTING_KEY`       | Routing key for DLX binding        |

**Run the consumer**

```bash
python amqp_consumers/raven_consumer.py
```

## Requirements

```
fastapi
uvicorn
pandas
pika
psycopg2
```

## Running the API

```bash
uvicorn app.main:app --reload
```
