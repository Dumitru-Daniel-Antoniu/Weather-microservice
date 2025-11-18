import grpc
import requests

from concurrent import futures

from core.config import WEATHER_API_KEY, WEATHER_API_URL

from server import weather_pb2_grpc
from server.weather_pb2 import CityWeatherDataResponse


class WeatherDataService(
    weather_pb2_grpc.WeatherDataServicer
):
    def Weather(self, request, context):
        parameters = {
            "q": request.city,
            "appid": WEATHER_API_KEY,
            "units": "metric"
        }

        try:
            response = requests.get(WEATHER_API_URL, params=parameters)
            response.raise_for_status()

            response_json = response.json()

            weather_info = {
                "city_name": request.city,
                "temperature": response_json.get("main", {}).get("temp", 18.0),
                "weather_description": response_json.get("weather", [{}])[0].get("description", "no description"),
                "humidity": response_json.get("main", {}).get("humidity", 0),
                "wind_speed": response_json.get("wind", {}).get("speed", 0.0),
            }

            return CityWeatherDataResponse(**weather_info)

        except requests.exceptions.HTTPError as e:
            if response.status_code == 404:
                context.set_details(f"City '{request.city}' not found.")
                context.set_code(grpc.StatusCode.NOT_FOUND)
            elif response.status_code == 401:
                context.set_details("Invalid API key.")
                context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            elif response.status_code == 429:
                context.set_details("API rate limit exceeded.")
                context.set_code(grpc.StatusCode.RESOURCE_EXHAUSTED)
            elif response.status_code >= 500:
                context.set_details("Weather API server error.")
                context.set_code(grpc.StatusCode.UNAVAILABLE)
            else:
                context.set_details(f"HTTP error occurred: {str(e)}")
                context.set_code(grpc.StatusCode.UNKNOWN)

        except requests.exceptions.ConnectionError:
            context.set_details("Network connection error.")
            context.set_code(grpc.StatusCode.UNAVAILABLE)

        except ValueError:
            context.set_details("Invalid or malformed response from weather API.")
            context.set_code(grpc.StatusCode.INTERNAL)

        except Exception as e:
            context.set_details(f"An unexpected error occurred: {str(e)}")
            context.set_code(grpc.StatusCode.UNKNOWN)

        return None


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    weather_pb2_grpc.add_WeatherDataServicer_to_server(
        WeatherDataService(), server
    )

    server.add_insecure_port("[::]:50051")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
