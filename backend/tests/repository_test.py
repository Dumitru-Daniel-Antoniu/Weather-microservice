import pytest

from datetime import datetime

from pymongo import errors

from repository import weather_repository

from unittest.mock import AsyncMock


class FakeCollection:
    def __init__(self, insert_side_effect=None, docs=None):
        self.insert_one = AsyncMock(side_effect=insert_side_effect)
        self._docs = docs or []

    def find(self, query):
        class Cursor:
            def __init__(self, docs):
                self._docs = docs
            def sort(self, *_):
                return self
            def limit(self, *_):
                return self
            def __aiter__(self):
                async def gen():
                    for d in self._docs:
                        yield d
                return gen()
        return Cursor(self._docs)


class FakeDB:
    def __init__(self, collection):
        self._collection = collection
    def __getitem__(self, name):
        return self._collection


class FakeClient:
    def __init__(self, db):
        self._db = db
    def __getitem__(self, name):
        return self._db


@pytest.mark.asyncio
async def test_insert_weather_success(monkeypatch):
    coll = FakeCollection()
    db = FakeDB(coll)
    client = FakeClient(db)

    monkeypatch.setattr(weather_repository, "client", client)

    await weather_repository.insert_weather("testdb", "testcol", {"a": 1})
    coll.insert_one.assert_awaited_once()


@pytest.mark.asyncio
async def test_insert_weather_server_timeout(monkeypatch):
    exc = errors.ServerSelectionTimeoutError("timeout")

    coll = FakeCollection(insert_side_effect=exc)
    db = FakeDB(coll)
    client = FakeClient(db)

    monkeypatch.setattr(weather_repository, "client", client)

    with pytest.raises(RuntimeError) as e:
        await weather_repository.insert_weather("testdb", "testcol", {"a": 1})
    assert "Failed to connect to MongoDB" in str(e.value)


@pytest.mark.asyncio
async def test_insert_weather_operation_failure(monkeypatch):
    exc = errors.OperationFailure("operation failure")

    coll = FakeCollection(insert_side_effect=exc)
    db = FakeDB(coll)
    client = FakeClient(db)

    monkeypatch.setattr(weather_repository, "client", client)

    with pytest.raises(RuntimeError) as e:
        await weather_repository.insert_weather("testdb", "testcol", {"a": 1})
    assert "MongoDB operation failed" in str(e.value)


@pytest.mark.asyncio
async def test_get_history_returns_documents(monkeypatch):
    docs = [
        {"date": "2023-01-02 00:00:00", "temperature": 1, "humidity": 10, "wind_speed": 0.5},
        {"date": "2023-01-03 00:00:00", "temperature": 2, "humidity": 20, "wind_speed": 1.5},
    ]

    coll = FakeCollection(docs=docs)
    db = FakeDB(coll)
    client = FakeClient(db)

    monkeypatch.setattr(weather_repository, "client", client)

    results = await weather_repository.get_history("testdb", "testcol", "citytest", "2023-01-01", "2023-12-31")

    assert isinstance(results, list)
    assert len(results) == 2

    results_sorted = sorted(results, key=lambda r: datetime.strptime(r["date"], "%Y-%m-%d %H:%M:%S"))
    assert results_sorted[0]["date"] == "2023-01-02 00:00:00"


@pytest.mark.asyncio
async def test_get_history_server_timeout(monkeypatch):
    def bad_find(query):
        raise errors.ServerSelectionTimeoutError("timeout")

    class BadCollection:
        def find(self, q):
            return bad_find(q)

    db = FakeDB(BadCollection())
    client = FakeClient(db)
    monkeypatch.setattr(weather_repository, "client", client)

    with pytest.raises(RuntimeError) as e:
        await weather_repository.get_history("testdb", "testcol", "cityexample", "s", "e")

    assert "Failed to connect to MongoDB" in str(e.value)
