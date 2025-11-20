import asyncio
import grpc
import weather_pb2
import weather_pb2_grpc

from core.config import GRPC_API_KEY

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

import logging
logging.basicConfig(level=logging.INFO)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
            logging.info(f"Sending WeatherHistory request for city: {city}, start_date: {start_date}, end_date: {end_date}")
            logging.info(f"Using API Key: {GRPC_API_KEY}")
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
            logging.info("gRPC error occurred: %s", e.details())
            return {"entries": [], "error": f"gRPC error: {e.details()}"}
