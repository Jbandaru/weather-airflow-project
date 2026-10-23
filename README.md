# Weather Data Pipeline: Apache Airflow, Docker & PostgreSQL

## Overview

An automated data engineering project that retrieves current weather observations from the [Open-Meteo API](https://open-meteo.com/), orchestrates ingestion with Apache Airflow, and stores the results in PostgreSQL.

The project demonstrates API integration, workflow orchestration, containerization, database operations, logging, error handling, and retry configuration.

## Architecture

```text
Open-Meteo Weather API
          |
          v
Python Ingestion Pipeline
          |
          v
Apache Airflow DAG
          |
          v
PostgreSQL (weather_db)
```

The services run in Docker containers managed by Docker Compose.

## Technology Stack

- **Python** — API integration and data ingestion
- **Open-Meteo API** — Weather data source
- **Apache Airflow 3.1.7** — Workflow orchestration
- **PostgreSQL 16** — Weather observation storage
- **Docker & Docker Compose** — Containerization
- **Requests** — HTTP API calls
- **Psycopg 3** — PostgreSQL connectivity

## Features

- Retrieves current weather for San Francisco, California.
- Captures temperature, relative humidity, precipitation, and wind speed.
- Stores observations with timestamps in PostgreSQL.
- Uses a unique location-and-timestamp constraint to prevent duplicate observations.
- Logs pipeline progress and failures.
- Configures two Airflow retries with a two-minute delay.
- Schedules the DAG every 30 minutes.

## Database Schema

The `weather_observations` table stores:

| Column | Description |
|---|---|
| `id` | Unique observation identifier |
| `location` | Location name |
| `latitude` | Latitude coordinate |
| `longitude` | Longitude coordinate |
| `temperature_c` | Temperature in Celsius |
| `humidity_percent` | Relative humidity percentage |
| `precipitation_mm` | Precipitation in millimeters |
| `wind_speed_kmh` | Wind speed in kilometers per hour |
| `observed_at` | Weather observation timestamp |
| `created_at` | Database insertion timestamp |

Duplicate observations for the same location and observation timestamp are skipped.

## Prerequisites

- Docker Desktop
- Git
- A terminal
- Internet access to reach the Open-Meteo API

## Setup

Clone the repository:

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd weather-airflow-project
```

Create a `.env` file if your Docker Compose configuration requires one. Use the environment variables expected by your Compose file, and never commit secrets.

Build the custom Airflow image:

```bash
docker compose build
```

Initialize Airflow if this is a fresh installation:

```bash
docker compose up airflow-init
```

Start the services:

```bash
docker compose up -d
```

Check service status:

```bash
docker compose ps
```

Open the Airflow UI at:

`http://localhost:8080`

The default Airflow Compose configuration may use development credentials. Change them before exposing the service beyond your local machine.

## Run the Pipeline

1. Open the Airflow UI.
2. Find the `weather_ingestion` DAG.
3. Unpause the DAG.
4. Trigger a manual run to test the workflow.
5. Inspect task logs and confirm the run succeeds.

The DAG is configured to run every 30 minutes.

## Verify Stored Data

Run:

```bash
docker compose exec weather-db \
  psql -U weather_user -d weather_db \
  -c "SELECT id, location, temperature_c, humidity_percent, observed_at FROM weather_observations ORDER BY id DESC LIMIT 10;"
```

## Useful Commands

Check service status:

```bash
docker compose ps
```

View Airflow scheduler logs:

```bash
docker compose logs --tail=100 airflow-scheduler
```

Stop services without deleting database volumes:

```bash
docker compose stop
```

Restart services:

```bash
docker compose start
```

## Future Improvements

- Consolidate duplicated pipeline code into a shared Python module.
- Move credentials into environment variables or a secrets manager.
- Add automated tests and data-quality checks.
- Add API and database connection health checks.
- Add monitoring and failure notifications.
- Support multiple locations and historical weather data.
- Add CI checks and publish project architecture diagrams.

## Disclaimer

This is a local learning and portfolio project. The supplied database credentials are intended only for local development and should not be reused in production.

