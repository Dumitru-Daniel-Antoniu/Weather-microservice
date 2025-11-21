import pytest

from server.weather_server import WeatherDataService

from unittest.mock import AsyncMock, Mock, patch


class ExampleResp:
    def raise_for_status(self): pass
    def json(self): return {"example": "ok"}


class Req:
    def __init__(self, city="", start_date=None, end_date=None):
        self.city = city
        self.start_date = start_date
        self.end_date = end_date


@pytest.mark.asyncio
async def test_weather_success_calls():
    svc = WeatherDataService()
    city = "London"
    expected = {
        "city_name": city,
        "temperature": 10.5,
        "weather_description": "clear",
        "humidity": 55,
        "wind_speed": 3.2,
    }

    with patch("server.weather_server.httpx.AsyncClient.get", new=AsyncMock(return_value=ExampleResp())), \
         patch("server.weather_server.process_api_response", new=AsyncMock(return_value=expected)), \
         patch("server.weather_server.add_weather", new=AsyncMock()):

        resp = await svc.Weather(Req(city), None)
        assert getattr(resp, "city_name", None) == expected["city_name"]
        assert getattr(resp, "temperature", None) == expected["temperature"]
        assert getattr(resp, "weather_description", None) == expected["weather_description"]
        assert getattr(resp, "humidity", None) == expected["humidity"]
        assert getattr(resp, "wind_speed", None) == expected["wind_speed"]


@pytest.mark.asyncio
async def test_weather_exception_calls():
    svc = WeatherDataService()
    city = "Paris"

    with patch("server.weather_server.httpx.AsyncClient.get", new=AsyncMock(return_value=ExampleResp())), \
         patch("server.weather_server.process_api_response", new=AsyncMock(side_effect=Exception("fail"))), \
         patch("server.weather_server.handle_weather_exception", new=Mock()) as mock_handler:

        resp = await svc.Weather(Req(city), None)
        mock_handler.assert_called()
        assert getattr(resp, "city_name", "") in ("", None)


@pytest.mark.asyncio
async def test_weather_history_returns_entries():
    svc = WeatherDataService()
    city = "Berlin"
    sample_entries = [
        {"date": "2025-01-01 00:00:00", "temperature": 1.1, "humidity": 10, "wind_speed": 0.5},
        {"date": "2025-01-02 00:00:00", "temperature": 2.2, "humidity": 20, "wind_speed": 1.5},
    ]

    with patch("server.weather_server.get_weather_history", new=AsyncMock(return_value=sample_entries)):
        req = Req(city=city, start_date="2025-01-01 00:00:00", end_date="2025-01-02 23:59:59")
        resp = await svc.WeatherHistory(req, None)
        assert hasattr(resp, "entries")
        assert len(resp.entries) == 2

        assert resp.entries[0].date == sample_entries[0]["date"]
        assert resp.entries[0].temperature == sample_entries[0]["temperature"]
        assert resp.entries[0].humidity == sample_entries[0]["humidity"]
        assert resp.entries[0].wind_speed == sample_entries[0]["wind_speed"]

        assert resp.entries[1].date == sample_entries[1]["date"]
        assert resp.entries[1].temperature == sample_entries[1]["temperature"]
        assert resp.entries[1].humidity == sample_entries[1]["humidity"]
        assert resp.entries[1].wind_speed == sample_entries[1]["wind_speed"]
