import grpc
import requests

from concurrent import futures

from core.config import COLLECTION_NAME, DATABASE_NAME, WEATHER_API_KEY, WEATHER_API_URL

from db.session import insert_weather_data

from weather_pb2_grpc import WeatherDataServicer, add_WeatherDataServicer_to_server
from weather_pb2 import CityWeatherDataResponse


class WeatherDataService(
    WeatherDataServicer
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

            insert_weather_data(DATABASE_NAME, COLLECTION_NAME, request.city, weather_info)

            return CityWeatherDataResponse(**weather_info)

        except requests.exceptions.RequestException as e:
            match e:
                case requests.exceptions.HTTPError():
                    if response.status_code == 401:
                        context.set_details("Invalid API key.")
                        context.set_code(grpc.StatusCode.UNAUTHENTICATED)
                    elif response.status_code == 404:
                        context.set_details(f"City '{request.city}' not found.")
                        context.set_code(grpc.StatusCode.NOT_FOUND)
                    elif response.status_code == 429:
                        context.set_details("API rate limit exceeded.")
                        context.set_code(grpc.StatusCode.RESOURCE_EXHAUSTED)
                    elif response.status_code >= 500:
                        context.set_details("Weather API server error.")
                        context.set_code(grpc.StatusCode.UNAVAILABLE)
                    else:
                        context.set_details(f"HTTP error occurred: {str(e)}")
                        context.set_code(grpc.StatusCode.UNKNOWN)

                case requests.exceptions.ConnectionError():
                    context.set_details("Network connection error.")
                    context.set_code(grpc.StatusCode.UNAVAILABLE)

                case requests.exceptions.Timeout():
                    context.set_details("The request to the weather API timed out.")
                    context.set_code(grpc.StatusCode.DEADLINE_EXCEEDED)

                case _:
                    context.set_details(f"An error occurred while requesting weather data: {str(e)}")
                    context.set_code(grpc.StatusCode.UNKNOWN)

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


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_WeatherDataServicer_to_server(
        WeatherDataService(), server
    )

    server.add_insecure_port("[::]:50051")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
