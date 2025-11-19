import os

from dotenv import load_dotenv


load_dotenv()

WEATHER_API_URL = os.getenv("WEATHER_API_URL")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
GRPC_API_KEY = os.getenv("GRPC_API_KEY")
MONGODB_USERNAME = os.getenv("MONGODB_USERNAME")
MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD")
MONGODB_PORT = os.getenv("MONGODB_PORT")
MONGODB_HOST = os.getenv("MONGODB_HOST")
DATABASE_NAME = os.getenv("DATABASE_NAME")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")
