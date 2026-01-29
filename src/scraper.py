"""
Weather scraper module for fetching weather data from OpenWeatherMap API.
"""
import requests
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, List
from .config import API_KEY, BASE_URL, REQUEST_TIMEOUT

logger = logging.getLogger(__name__)

# East African Time (UTC+3)
EAT = timezone(timedelta(hours=3))


class WeatherScraper:
    """Handles weather data scraping from OpenWeatherMap API."""
    
    def __init__(self, api_key: str = None, base_url: str = None, timeout: int = None):
        """
        Initialize the weather scraper.
        
        Args:
            api_key: OpenWeatherMap API key (defaults to config value)
            base_url: API base URL (defaults to config value)
            timeout: Request timeout in seconds (defaults to config value)
        """
        self.api_key = api_key or API_KEY
        self.base_url = base_url or BASE_URL
        self.timeout = timeout or REQUEST_TIMEOUT
        
        if not self.api_key:
            raise ValueError("API key is required. Set OPENWEATHER_API_KEY in .env file.")
    
    def fetch_weather(self, location_name: str) -> Optional[Dict]:
        """
        Fetch weather data for a given location.
        
        Args:
            location_name: Name of the location (e.g., "Nabuti, Mukono, UG")
            
        Returns:
            Dictionary containing weather data or None if request fails
        """
        params = {
            "q": location_name,
            "appid": self.api_key,
            "units": "metric"
        }
        
        try:
            response = requests.get(
                self.base_url,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            weather_data = response.json()
            
            return {
                "timestamp": datetime.now(EAT).strftime("%Y-%m-%d %H:%M:%S"),
                "location": weather_data.get("name"),
                "weather": weather_data.get("weather", [{}])[0].get("description"),
                "temperature(C)": weather_data.get("main", {}).get("temp"),
                "wind_speed(mps)": weather_data.get("wind", {}).get("speed"),
                "humidity(%)": weather_data.get("main", {}).get("humidity"),
                "pressure(hPa)": weather_data.get("main", {}).get("pressure"),
                "feels_like(C)": weather_data.get("main", {}).get("feels_like"),
                "visibility(m)": weather_data.get("visibility"),
                "clouds(%)": weather_data.get("clouds", {}).get("all"),
            }
            
        except requests.exceptions.Timeout:
            logger.error(f"Request timeout for location: {location_name}")
            return None
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error for location {location_name}: {e}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get weather details for {location_name}: {e}")
            return None
        except (KeyError, IndexError) as e:
            logger.error(f"Error parsing response for {location_name}: {e}")
            return None
    
    def fetch_multiple_locations(self, locations: List[Dict[str, str]]) -> List[Dict]:
        """
        Fetch weather data for multiple locations.
        
        Args:
            locations: List of location dictionaries with 'name' key
            
        Returns:
            List of weather data dictionaries
        """
        weather_data = []
        
        for location in locations:
            location_name = location.get("name")
            if not location_name:
                logger.warning(f"Skipping location with missing name: {location}")
                continue
                
            result = self.fetch_weather(location_name)
            if result:
                weather_data.append(result)
                logger.info(f"Weather data for {result['location']} fetched successfully")
            else:
                logger.warning(f"Failed to fetch weather data for {location_name}")
        
        return weather_data
