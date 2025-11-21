from datetime import datetime

from repository.weather_repository import insert_weather

from tzlocal import get_localzone


async def add_weather(
    database_name: str,
    collection_name: str,
    city: str,
    weather_info: dict
):
    """Adds current weather data to the database."""

    try:
        if not city:
            raise ValueError("City name must be provided.")

        required_fields = ["temperature", "weather_description", "humidity", "wind_speed"]
        for field in required_fields:
            if field not in weather_info:
                raise ValueError(f"Missing required field in weather_info: {field}")

        local_timezone = get_localzone()
        local_time = datetime.now(local_timezone).strftime("%Y-%m-%d %H:%M:%S")

        document = {
            "city": city,
            "date": local_time,
            "temperature": weather_info["temperature"],
            "weather_description": weather_info["weather_description"],
            "humidity": weather_info["humidity"],
            "wind_speed": weather_info["wind_speed"]
        }

        await insert_weather(database_name, collection_name, document)

    except RuntimeError as e:
        raise RuntimeError(f"Runtime error occurred: {e}") from e
  