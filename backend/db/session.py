from core.config import MONGODB_HOST, MONGODB_PASSWORD, MONGODB_PORT, MONGODB_USERNAME

from motor.motor_asyncio import AsyncIOMotorClient


MONGO_URI = f"mongodb://{MONGODB_USERNAME}:{MONGODB_PASSWORD}@{MONGODB_HOST}:{MONGODB_PORT}"
client = AsyncIOMotorClient(MONGO_URI)
