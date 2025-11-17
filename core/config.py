import os

from dotenv import load_dotenv


load_dotenv()

WEATHER_API_URL = os.getenv("WEATHER_API_URL")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
