import asyncio
import grpc
import httpx

from core.config import GRPC_API_KEY, COLLECTION_NAME, DATABASE_NAME, WEATHER_API_KEY, WEATHER_API_URL

from security.access import APIKeyInterceptor

from service.api_response_data_processing import process_api_response
from service.current_weather_data import add_weather
from service.weather_history_data import get_weather_history

from utils.exception_handler import handle_weather_exception

from weather_pb2_grpc import WeatherDataServicer, add_WeatherDataServicer_to_server
from weather_pb2 import CityWeatherDataResponse, HistoryEntry, HistoryResponse


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

                weather_info = await process_api_response(request.city, response_json)

                await add_weather(DATABASE_NAME, COLLECTION_NAME, request.city, weather_info)

                return CityWeatherDataResponse(**weather_info)

        except Exception as e:
            handle_weather_exception(context, e, request_city=request.city)

        return CityWeatherDataResponse()


    async def WeatherHistory(self, request, context):
        try:
            city = request.city
            start_date = request.start_date
            end_date = request.end_date

            if not city or not start_date or not end_date:
                return HistoryResponse(entries=[], error="Missing required parameters.")

            results = await get_weather_history(DATABASE_NAME, COLLECTION_NAME, city, start_date, end_date)
            if not results:
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

            return HistoryResponse(entries=entries, error="")

        except ValueError as e:
            return HistoryResponse(entries=[], error=f"A value error occurred: {str(e)}")

        except RuntimeError as e:
            return HistoryResponse(entries=[], error=f"A runtime error occurred: {str(e)}")

        except Exception as e:
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
