import grpc

from weather_pb2 import CityRequest
from weather_pb2_grpc import WeatherDataStub


def main():
    city = input("Enter city name: ")

    channel = grpc.insecure_channel("localhost:50051")
    client = WeatherDataStub(channel)
    request = CityRequest(city=city)

    try:
        response = client.Weather(request)
        print("Weather data received:")
        print(f"City: {response.city_name}")
        print(f"Temperature: {response.temperature}°C")
        print(f"Weather: {response.weather_description}")
        print(f"Humidity: {response.humidity}%")
        print(f"Wind Speed: {response.wind_speed}")
    
    except grpc.RpcError as e:
        print("An error occurred:")
        print(f"Status Code: {e.code()}")
        print(f"Details: {e.details()}")


if __name__ == "__main__":
    main()
