import asyncio
import grpc
import httpx

from concurrent import futures

from core.config import GRPC_API_KEY, COLLECTION_NAME, DATABASE_NAME, WEATHER_API_KEY, WEATHER_API_URL

from db.session import get_weather_history, insert_weather_data

from security.access import APIKeyInterceptor

from security.access import APIKeyInterceptor

from weather_pb2_grpc import WeatherDataServicer, add_WeatherDataServicer_to_server
from weather_pb2 import CityWeatherDataResponse, HistoryEntry, HistoryResponse

import logging
logging.basicConfig(level=logging.INFO)

class WeatherDataService(
    WeatherDataServicer
):
    async def Weather(self, request, context):
        parameters = {
            "q": request.city,
            "appid": WEATHER_API_KEY,
            "units": "metric"
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(WEATHER_API_URL, params=parameters)
                response.raise_for_status()

                response_json = response.json()

                weather_info = {
                    "city_name": request.city,
                    "temperature": response_json.get("main", {}).get("temp", 18.0),
                    "weather_description": response_json.get("weather", [{}])[0].get("description", "no description"),
                    "humidity": response_json.get("main", {}).get("humidity", 0),
                    "wind_speed": response_json.get("wind", {}).get("speed", 0.0),
                }

                await insert_weather_data(DATABASE_NAME, COLLECTION_NAME, request.city, weather_info)

                return CityWeatherDataResponse(**weather_info)

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                context.set_details("Invalid API key.")
                context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            elif e.response.status_code == 404:
                context.set_details(f"City '{request.city}' not found.")
                context.set_code(grpc.StatusCode.NOT_FOUND)
            elif e.response.status_code == 429:
                context.set_details("API rate limit exceeded.")
                context.set_code(grpc.StatusCode.RESOURCE_EXHAUSTED)
            elif e.response.status_code >= 500:
                context.set_details("Weather API server error.")
                context.set_code(grpc.StatusCode.UNAVAILABLE)
            else:
                context.set_details(f"HTTP error occurred: {str(e)}")
                context.set_code(grpc.StatusCode.UNKNOWN)

        except httpx.RequestError as e:
            context.set_details(f"HTTP request error: {str(e)}")
            context.set_code(grpc.StatusCode.UNAVAILABLE)

        except ValueError:
            context.set_details("Invalid or malformed response from weather API.")
            context.set_code(grpc.StatusCode.INTERNAL)

        except RuntimeError as e:
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)

        except Exception as e:
            context.set_details(f"An unexpected error occurred: {str(e)}")
            context.set_code(grpc.StatusCode.UNKNOWN)

        return CityWeatherDataResponse()


    async def WeatherHistory(self, request, context):
        try:
            city = request.city
            start_date = request.start_date
            end_date = request.end_date
            logging.info(f"Received WeatherHistory request for city: {city}, start_date: {start_date}, end_date: {end_date}")

            if not city or not start_date or not end_date:
                logging.info("Missing required parameters in WeatherHistory request.")
                return HistoryResponse(entries=[], error="Missing required parameters.")

            results = await get_weather_history(DATABASE_NAME, COLLECTION_NAME, city, start_date, end_date)
            if not results:
                logging.info("No data found for the specified city and date range.")
                return HistoryResponse(entries=[], error="No data found for this city and period.")

            entries = [
                HistoryEntry(
                    date=entry["date"],
                    temperature=entry["temperature"],
                    humidity=entry["humidity"],
                    wind_speed=entry["wind_speed"]
                )
                for entry in results
            ]
            logging.info(f"Returning {len(entries)} history entries.")

            return HistoryResponse(entries=entries, error="")

        except Exception as e:
            logging.error(f"Error in WeatherHistory: {str(e)}")
            return HistoryResponse(entries=[], error=f"An unexpected error occurred: {str(e)}")


async def serve():
    server = grpc.aio.server(
        interceptors=[APIKeyInterceptor(GRPC_API_KEY)]
    )

    add_WeatherDataServicer_to_server(
        WeatherDataService(), server
    )

    server.add_insecure_port("[::]:50051")
    await server.start()
    await server.wait_for_termination()


if __name__ == "__main__":
    asyncio.run(serve())
