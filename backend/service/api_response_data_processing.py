

async def process_api_response(city: str, response_json: dict) -> dict:
    """Processes the API response and extracts relevant weather data."""
    try:
        if not city:
            raise ValueError("City name must be provided.")

        if not isinstance(response_json, dict):
            raise ValueError("API response is not a valid dictionary.")

        if "main" not in response_json or "weather" not in response_json or "wind" not in response_json:
            raise ValueError("API response is missing required weather data fields.")

        temperature = response_json.get("main", {}).get("temp", 10.0)
        description = response_json.get("weather", [{}])[0].get("description", "no description")
        humidity = response_json.get("main", {}).get("humidity", 0)
        wind_speed = response_json.get("wind", {}).get("speed", 0.0)

        weather_info = {
            "city_name": city,
            "temperature": temperature,
            "weather_description": description,
            "humidity": humidity,
            "wind_speed": wind_speed,
        }

        return weather_info

    except RuntimeError as e:
        raise RuntimeError(f"Runtime error occurred: {e}") from e