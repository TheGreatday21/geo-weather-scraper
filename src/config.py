"""
Configuration module for weather data pipeline.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Configuration
API_KEY = os.getenv("OPENWEATHER_API_KEY")
BASE_URL = os.getenv("OPENWEATHER_BASE_URL", "https://api.openweathermap.org/data/2.5/weather")
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "10"))

# Scraping Configuration
SCRAPE_DELAY_MINUTES = int(os.getenv("SCRAPE_DELAY_MINUTES", "3"))
SCRAPE_DELAY_SECONDS = SCRAPE_DELAY_MINUTES * 60
NUM_ITERATIONS = int(os.getenv("NUM_ITERATIONS", "10"))

# Data Storage Configuration
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
SAMPLES_DIR = DATA_DIR / "samples"
OUTPUT_FILENAME = os.getenv("OUTPUT_FILENAME", "weather_data.csv")

# Default locations to scrape
DEFAULT_LOCATIONS = [
    {"name": "Kirowoza, Mukono, UG"},
    {"name": "Bugujju, Mukono, UG"},
    {"name": "Seeta, Mukono, UG"},
    {"name": "Namilyango, Mukono, UG"},
    {"name": "Kyetume, Mukono, UG"},
    {"name": "Katosi, Mukono, UG"},
]

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
