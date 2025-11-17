import grpc
import weather_pb2_grpc

from concurrent import futures
from weather_pb2 import (
    CityRequest,
    CityWeatherDataResponse
)


weather_by_city = {
    "Paris": {
        "temperature": 22,
        "weather_description": "Sunny",
        "humidity": 45,
        "wind_speed": "10 km/h"
    },
    "Barcelona": {
        "temperature": 18,
        "weather_description": "Cloudy",
        "humidity": 55,
        "wind_speed": "15 km/h"
    },
    "Roma": {
        "temperature": 20,
        "weather_description": "Partly Cloudy",
        "humidity": 50,
        "wind_speed": "12 km/h"
    },
    "London": {
        "temperature": 19,
        "weather_description": "Rainy",
        "humidity": 60,
        "wind_speed": "20 km/h"
    }
}


class WeatherDataService(
    weather_pb2_grpc.WeatherDataServicer
):
    def Weather(self, request, context):
        if request.city not in weather_by_city:
            context.abort(grpc.StatusCode.NOT_FOUND, "City not found")

        weather_info = weather_by_city[request.city]
        weather_info["city_name"] = request.city

        return CityWeatherDataResponse(**weather_info)


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
