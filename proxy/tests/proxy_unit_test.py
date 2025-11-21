import grpc
import pytest

from application import app

from core.config import REQUEST_HOST, REQUEST_PORT

from fastapi.testclient import TestClient

from unittest.mock import AsyncMock, patch


client = TestClient(app)

BASE_URL = f"http://{REQUEST_HOST}:{REQUEST_PORT}"


class ExampleAioRpcError(grpc.aio.AioRpcError):
    def __init__(self, message: str):
        self._message = message
    def details(self) -> str:
        return self._message


@pytest.mark.asyncio
async def test_get_weather_success():
    with patch("application.weather_pb2_grpc.WeatherDataStub") as mock_stub_cls, \
         patch("application.grpc.aio.insecure_channel") as mock_insecure_channel:

        mock_channel = AsyncMock()
        mock_insecure_channel.return_value.__aenter__.return_value = mock_channel

        stub_instance = mock_stub_cls.return_value
        mock_response = AsyncMock()
        mock_response.city_name = "London"
        mock_response.temperature = 20.5
        mock_response.weather_description = "clear sky"
        mock_response.humidity = 60
        mock_response.wind_speed = 5.2
        stub_instance.Weather = AsyncMock(return_value=mock_response)

        response = client.get("/api/weather", params={"city": "London"})
        assert response.status_code == 200
        data = response.json()
        assert data.get("city_name") == "London"
        assert data.get("temperature") == 20.5
        assert data.get("weather_description") == "clear sky"
        assert data.get("humidity") == 60
        assert data.get("wind_speed") == 5.2


@pytest.mark.asyncio
async def test_get_weather_grpc_error():
    with patch("application.weather_pb2_grpc.WeatherDataStub") as mock_stub_cls, \
         patch("application.grpc.aio.insecure_channel") as mock_insecure_channel:

        mock_channel = AsyncMock()
        mock_insecure_channel.return_value.__aenter__.return_value = mock_channel

        stub_instance = mock_stub_cls.return_value
        stub_instance.Weather = AsyncMock(side_effect=ExampleAioRpcError("gRPC error"))

        response = client.get("/api/weather", params={"city": "London"})
        assert response.status_code == 200

        data = response.json()
        assert data.get("error") == "Error: gRPC error"


@pytest.mark.asyncio
async def test_get_history_success():
    with patch("application.weather_pb2_grpc.WeatherDataStub") as mock_stub_cls, \
         patch("application.grpc.aio.insecure_channel") as mock_insecure_channel:

        mock_channel = AsyncMock()
        mock_insecure_channel.return_value.__aenter__.return_value = mock_channel

        stub_instance = mock_stub_cls.return_value

        entry = AsyncMock()
        entry.date = "2023-11-21 10:00:00"
        entry.temperature = 15.0
        entry.humidity = 55
        entry.wind_speed = 3.0

        mock_response = AsyncMock()
        mock_response.entries = [entry]
        mock_response.error = ""

        stub_instance.WeatherHistory = AsyncMock(return_value=mock_response)

        response = client.get("/api/history", params={
            "city": "London",
            "start_date": "2023-11-20 00:00:00",
            "end_date": "2023-11-21 23:59:59"
        })

        assert response.status_code == 200
        data = response.json()

        assert "entries" in data
        weather_data = data["entries"][0]

        assert weather_data.get("date") == "2023-11-21 10:00:00"
        assert weather_data.get("temperature") == 15.0
        assert weather_data.get("humidity") == 55
        assert weather_data.get("wind_speed") == 3.0


@pytest.mark.asyncio
async def test_get_history_grpc_error():
    with patch("application.weather_pb2_grpc.WeatherDataStub") as mock_stub_cls, \
         patch("application.grpc.aio.insecure_channel") as mock_insecure_channel:

        mock_channel = AsyncMock()
        mock_insecure_channel.return_value.__aenter__.return_value = mock_channel

        stub_instance = mock_stub_cls.return_value
        stub_instance.WeatherHistory = AsyncMock(side_effect=ExampleAioRpcError("gRPC error"))

        response = client.get("/api/history", params={
            "city": "London",
            "start_date": "2023-11-20 00:00:00",
            "end_date": "2023-11-21 23:59:59"
        })
        assert response.status_code == 200
        data = response.json()
        assert data.get("entries") == []
        assert data.get("error") == "Error: gRPC error"
