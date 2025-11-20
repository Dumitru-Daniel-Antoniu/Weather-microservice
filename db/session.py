from core.config import MONGODB_HOST, MONGODB_PASSWORD, MONGODB_PORT, MONGODB_USERNAME

from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorClient

from pymongo import errors

from tzlocal import get_localzone


MONGO_URI = f"mongodb://{MONGODB_USERNAME}:{MONGODB_PASSWORD}@{MONGODB_HOST}:{MONGODB_PORT}"
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
