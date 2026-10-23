import logging
import requests
import psycopg
from datetime import datetime
from zoneinfo import ZoneInfo

# Configure logging for Airflow task logs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)


# Open-Meteo API configuration
API_URL = "https://api.open-meteo.com/v1/forecast"

LOCATION = "San Francisco"
LATITUDE = 37.7749
LONGITUDE = -122.4194
TIMEZONE = "America/Los_Angeles"

# Local development database configuration
DB_CONFIG = {
    "host": "weather-db",
    "port": 5432,
    "dbname": "weather_db",
    "user": "weather_user",
    "password": "weather_dev_password",
}


def fetch_weather():
    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "current": [
            "temperature_2m",
            "relative_humidity_2m",
            "precipitation",
            "wind_speed_10m",
        ],
        "timezone": TIMEZONE,
    }

    logger.info("Requesting current weather for %s", LOCATION)

    response = requests.get(API_URL, params=params, timeout=30)
    response.raise_for_status()

    data = response.json()
    weather = data["current"]

    logger.info("Weather data fetched successfully. Observation time: %s", weather["time"])

    return weather


def save_weather(weather):
    observed_at = datetime.fromisoformat(
        weather["time"]
    ).replace(tzinfo=ZoneInfo(TIMEZONE))

    logger.info("Connecting to PostgreSQL to save weather data")

    with psycopg.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO weather_observations (
                    location,
                    latitude,
                    longitude,
                    temperature_c,
                    humidity_percent,
                    precipitation_mm,
                    wind_speed_kmh,
                    observed_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (location, observed_at)
                DO NOTHING
                RETURNING id;
                """,
                (
                    LOCATION,
                    LATITUDE,
                    LONGITUDE,
                    weather["temperature_2m"],
                    weather["relative_humidity_2m"],
                    weather["precipitation"],
                    weather["wind_speed_10m"],
                    observed_at,
                ),
            )

            inserted_row = cur.fetchone()

    if inserted_row:
        logger.info(
            "Weather observation saved successfully. ID: %s",
            inserted_row[0],
        )
    else:
        logger.info(
            "Observation already exists for %s. Skipping duplicate.",
            observed_at,
        )


def main():
    try:
        weather = fetch_weather()
        logger.info("Fetched weather data: %s", weather)
        save_weather(weather)
        logger.info("Weather data saved successfully.")
    except Exception:
        logger.exception("Weather pipeline failed: %s")
        raise


if __name__ == "__main__":
    main()
