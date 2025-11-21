import pytest
import uuid

from core.config import COLLECTION_NAME, DATABASE_NAME, MONGODB_HOST, MONGODB_PASSWORD, MONGODB_PORT, MONGODB_USERNAME

from db import session

from motor.motor_asyncio import AsyncIOMotorClient

from pymongo import MongoClient

from repository import weather_repository


TEST_DB = DATABASE_NAME
TEST_COLLECTION = COLLECTION_NAME


@pytest.mark.asyncio
async def test_insert_and_get_history_integration():
    host = MONGODB_HOST
    port = MONGODB_PORT
    admin_user = MONGODB_USERNAME
    admin_pass = MONGODB_PASSWORD

    if not admin_user or not admin_pass:
        pytest.skip("Admin Mongo credentials not provided (MONGODB_ROOT_USERNAME/MONGODB_ROOT_PASSWORD).")

    admin_uri = f"mongodb://{admin_user}:{admin_pass}@{host}:{port}/?authSource=admin"
    admin_client = MongoClient(admin_uri)

    original_client = session.client
    session.client = AsyncIOMotorClient(admin_uri)

    try:
        db = session.client[TEST_DB]
        coll = db[TEST_COLLECTION]
        probe = {"_probe": uuid.uuid4().hex}
        await coll.insert_one(probe)
        await coll.delete_one(probe)

    except Exception:
        try:
            await session.client.close()
        except Exception:
            pass
        session.client = original_client
        admin_client.close()
        pytest.skip("Admin credentials provided but unable to write to MongoDB with them.")

    try:
        city = f"city_{uuid.uuid4().hex[:8]}"
        doc = {
            "city": city,
            "date": "2025-01-01 00:00:00",
            "temperature": 12.3,
            "humidity": 50,
            "wind_speed": 2.5,
        }

        await weather_repository.insert_weather(TEST_DB, TEST_COLLECTION, doc)

        results = await weather_repository.get_history(
            TEST_DB,
            TEST_COLLECTION,
            city,
            "2024-01-01 00:00:00",
            "2026-01-01 00:00:00",
        )

        assert isinstance(results, list)
        assert any(r.get("temperature") == 12.3 and r.get("date") == "2025-01-01 00:00:00" for r in results)

        db = session.client[TEST_DB]
        coll = db[TEST_COLLECTION]
        await coll.delete_many({"city": city})

    finally:
        try:
            await session.client.close()
        except Exception:
            pass

        session.client = original_client
        admin_client.close()
