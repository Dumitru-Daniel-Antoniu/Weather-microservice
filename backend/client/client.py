import asyncio
import grpc

from core.config import GRPC_API_KEY, GRPC_CLIENT_HOST, GRPC_PORT

from weather_pb2 import CityRequest
from weather_pb2_grpc import WeatherDataStub


async def main():
    city = input("Enter city name: ")

    async with grpc.aio.insecure_channel(f"{GRPC_CLIENT_HOST}:{GRPC_PORT}") as channel:
        client = WeatherDataStub(channel)
        request = CityRequest(city=city)

        metadata = [("x-api-key", GRPC_API_KEY)]

        try:
            response = await client.Weather(request, metadata=metadata)
            print("Weather data received:")
            print(f"City: {response.city_name}")
            print(f"Temperature: {response.temperature}°C")
            print(f"Weather: {response.weather_description}")
            print(f"Humidity: {response.humidity}%")
            print(f"Wind Speed: {response.wind_speed}")
        
        except grpc.aio.AioRpcError as e:
            print("An error occurred:")
            print(f"Status Code: {e.code()}")
            print(f"Details: {e.details()}")

        except Exception as e:
            print("An error occurred:")
            print(f"Status Code: {e.code()}")
            print(f"Details: {e.details()}")


if __name__ == "__main__":
    asyncio.run(main())
