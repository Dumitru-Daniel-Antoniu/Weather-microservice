import logging

from core.config import MONGODB_HOST, MONGODB_PASSWORD, MONGODB_PORT, MONGODB_USERNAME

from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorClient

from pymongo import errors

from tzlocal import get_localzone

logging.basicConfig(level=logging.INFO)


logging.info("Connecting to MongoDB...")
logging.info(f"Host: {MONGODB_HOST}, Port: {MONGODB_PORT}, Username: {MONGODB_USERNAME}")
MONGO_URI = f"mongodb://{MONGODB_USERNAME}:{MONGODB_PASSWORD}@{MONGODB_HOST}:{MONGODB_PORT}"
logging.info(f"MongoDB URI: {MONGO_URI}")
client = AsyncIOMotorClient(MONGO_URI)


async def insert_weather_data(
    database_name: str,
    collection_name: str,
    city: str,
    weather_info: dict
) -> None:
    """Inserts weather data into the specified MongoDB collection."""
    try:
        db = client[database_name]
        collection = db[collection_name]

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

        await collection.insert_one(document)

    except errors.ServerSelectionTimeoutError as e:
        raise RuntimeError("Failed to connect to MongoDB") from e

    except errors.OperationFailure as e:
        raise RuntimeError("MongoDB operation failed") from e

    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred: {str(e)}") from e


async def get_weather_history(
    database_name: str,
    collection_name: str,
    city: str,
    start_date: str,
    end_date: str
):
    """Fetch weather history for a city in a date range."""
    db = client[database_name]
    collection = db[collection_name]

    try:
        query = {
            "city": city,
            "date": {"$gte": start_date, "$lte": end_date}
        }

        cursor = collection.find(query)
        results = []

        async for document in cursor:
            results.append({
                "date": document["date"],
                "temperature": document["temperature"],
                "humidity": document["humidity"],
                "wind_speed": document["wind_speed"]
            })
        return results

    except Exception as e:
        raise RuntimeError(f"Failed to fetch weather history: {str(e)}")
