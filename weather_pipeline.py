import requests
import psycopg
from datetime import datetime
from zoneinfo import ZoneInfo

# Open-Meteo API configuration
API_URL = "https://api.open-meteo.com/v1/forecast"

LOCATION = "San Francisco"
LATITUDE = 37.7749
LONGITUDE = -122.4194

# Local development database configuration
DB_CONFIG = {
    "host": "localhost",
    "port": 5433,
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
        "timezone": "America/Los_Angeles",
    }

    response = requests.get(API_URL, params=params, timeout=30)
    response.raise_for_status()

    data = response.json()
    return data["current"]


def save_weather(weather):
    observed_at = datetime.fromisoformat(
        weather["time"]
    ).replace(tzinfo=ZoneInfo("America/Los_Angeles"))

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
        print(f"Weather observation saved. ID: {inserted_row[0]}")
    else:
        print("This observation already exists; no duplicate inserted.")


def main():
    weather = fetch_weather()
    print("Fetched weather:", weather)
    save_weather(weather)


if __name__ == "__main__":
    main()
