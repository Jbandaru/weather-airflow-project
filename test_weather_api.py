import requests

url = "https://api.open-meteo.com/v1/forecast"

params = {
    "latitude": 37.7749,
    "longitude": -122.4194,
    "current": [
        "temperature_2m",
        "relative_humidity_2m",
        "precipitation",
        "wind_speed_10m"
    ],
    "timezone": "America/Los_Angeles"
}

response = requests.get(url, params=params, timeout=30)
response.raise_for_status()

data = response.json()

print("Location: San Francisco")
print("Current weather:")
print(data["current"])
