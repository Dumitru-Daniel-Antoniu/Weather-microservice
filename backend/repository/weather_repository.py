from db.session import client

from pymongo import errors


async def insert_weather(
    database_name: str,
    collection_name: str,
    document: dict
):
    """Inserts weather data into the specified MongoDB collection."""

    try:
        db = client[database_name]
        collection = db[collection_name]
        await collection.insert_one(document)

    except errors.ServerSelectionTimeoutError as e:
        raise RuntimeError("Failed to connect to MongoDB") from e

    except errors.OperationFailure as e:
        raise RuntimeError("MongoDB operation failed") from e

    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred: {str(e)}") from e


async def get_history(
    database_name: str,
    collection_name: str,
    city: str,
    start_date: str,
    end_date: str
):
    """Fetch weather history for a city in a date range."""

    try:
        db = client[database_name]
        collection = db[collection_name]

        query = {
            "city": {"$regex": f"^{city}$", "$options": "i"},
            "date": {"$gte": start_date, "$lte": end_date}
        }

        cursor = collection.find(query).sort("date", -1).limit(101)
        results = []

        async for document in cursor:
            results.append({
                "date": document["date"],
                "temperature": document["temperature"],
                "humidity": document["humidity"],
                "wind_speed": document["wind_speed"]
            })

        results.reverse()
        return results

    except errors.ServerSelectionTimeoutError as e:
        raise RuntimeError("Failed to connect to MongoDB") from e

    except errors.OperationFailure as e:
        raise RuntimeError("MongoDB operation failed") from e

    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred: {str(e)}") from e
