import pytest
import requests
import time

from application import app

from core.config import REQUEST_HOST, REQUEST_PORT

from fastapi.testclient import TestClient


client = TestClient(app)

BASE_URL = f"http://{REQUEST_HOST}:{REQUEST_PORT}"


def _wait_for(url: str):
    deadline = time.time() + 30
    last_exc = None
    while time.time() < deadline:
        try:
            r = requests.get(url, timeout=3)
            return r
        except Exception as e:
            last_exc = e
            time.sleep(1.0)
    raise RuntimeError(f"Service not available at {url}: {last_exc}")


@pytest.mark.asyncio
async def test_integration_get_weather():
    url = f"{BASE_URL}/api/weather"

    response = _wait_for(f"{url}?city=London")
    assert response.status_code == 200, f"unexpected status {response.status_code} body={response.text}"

    data = response.json()

    success_keys = {"city_name", "temperature", "weather_description", "humidity", "wind_speed"}
    assert ("error" in data) or success_keys.issubset(set(data.keys())), f"unexpected payload: {data}"


@pytest.mark.asyncio
async def test_integration_get_history():
    url = f"{BASE_URL}/api/history"

    params = {
        "city": "London",
        "start_date": "2023-01-01 00:00:00",
        "end_date": "2025-12-31 23:59:59"
    }

    response = _wait_for(f"{url}?city=London&start_date={params['start_date']}&end_date={params['end_date']}")
    assert response.status_code == 200, f"unexpected status {response.status_code} body={response.text}"

    data = response.json()

    if "error" in data and data.get("error"):
        assert isinstance(data.get("error"), str)
    else:
        assert "entries" in data and isinstance(data["entries"], list)
        if data["entries"]:
            first = data["entries"][0]
            assert "date" in first and "temperature" in first \
                    and "humidity" in first and "wind_speed" in first, f"unexpected entry: {first}"
