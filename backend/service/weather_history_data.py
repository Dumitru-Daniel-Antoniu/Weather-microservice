from repository.weather_repository import get_history


async def get_weather_history(
    database_name: str,
    collection_name: str,
    city: str,
    start_date: str,
    end_date: str
):
    """Fetches weather history for a city within a date range."""
    try:
        if not city:
            raise ValueError("City name must be provided.")

        if not start_date or not end_date:
            raise ValueError("Both start_date and end_date must be provided.")

        results = await get_history(
            database_name,
            collection_name,
            city,
            start_date,
            end_date
        )

        seen_dates = set()
        unique_results = []
        for entry in results:
            entry_date = entry["date"][:16]
            if entry_date not in seen_dates:
                unique_results.append(entry)
                seen_dates.add(entry_date)

        return unique_results

    except RuntimeError as e:
        raise RuntimeError(f"Runtime error occurred: {e}") from e
