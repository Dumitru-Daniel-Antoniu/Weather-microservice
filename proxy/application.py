import grpc
import weather_pb2
import weather_pb2_grpc

from core.config import GRPC_API_KEY

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/weather")
async def get_weather(city: str):
    async with grpc.aio.insecure_channel('weather_backend:50051') as channel:
        stub = weather_pb2_grpc.WeatherDataStub(channel)
        request = weather_pb2.CityRequest(city=city)

        try:
            response = await stub.Weather(
                request,
                metadata=[("x-api-key", GRPC_API_KEY)]
            )

            return {
                "city_name": response.city_name,
                "temperature": response.temperature,
                "weather_description": response.weather_description,
                "humidity": response.humidity,
                "wind_speed": response.wind_speed
            }

        except grpc.aio.AioRpcError as e:
            return {"error": f"Error: {e.details()}"}

@app.get("/api/history")
async def get_history(city: str, start_date: str, end_date: str):
    async with grpc.aio.insecure_channel('weather_backend:50051') as channel:
        stub = weather_pb2_grpc.WeatherDataStub(channel)
        request = weather_pb2.HistoryRequest(
            city=city,
            start_date=start_date,
            end_date=end_date
        )

        try:
            response = await stub.WeatherHistory(
                request,
                metadata=[("x-api-key", GRPC_API_KEY)]
            )
            return {
                "entries": [
                    {
                        "date": entry.date,
                        "temperature": entry.temperature,
                        "humidity": entry.humidity,
                        "wind_speed": entry.wind_speed
                    }
                    for entry in response.entries
                ],
                "error": response.error
            }

        except grpc.aio.AioRpcError as e:
            return {"entries": [], "error": f"Error: {e.details()}"}
