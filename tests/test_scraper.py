"""
Unit tests for weather scraper module.
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.scraper import WeatherScraper, EAT
from datetime import datetime


class TestWeatherScraper(unittest.TestCase):
    """Test cases for WeatherScraper class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.api_key = "test_api_key"
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"
        self.scraper = WeatherScraper(api_key=self.api_key, base_url=self.base_url)
    
    @patch('src.scraper.requests.get')
    def test_fetch_weather_success(self, mock_get):
        """Test successful weather data fetch."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "name": "Nabuti",
            "weather": [{"description": "clear sky"}],
            "main": {
                "temp": 25.5,
                "humidity": 60,
                "pressure": 1013,
                "feels_like": 26.0
            },
            "wind": {"speed": 3.2},
            "visibility": 10000,
            "clouds": {"all": 20}
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = self.scraper.fetch_weather("Nabuti, Mukono, UG")
        
        self.assertIsNotNone(result)
        self.assertEqual(result["location"], "Nabuti")
        self.assertEqual(result["temperature(C)"], 25.5)
        self.assertEqual(result["weather"], "clear sky")
        self.assertIn("timestamp", result)
    
    @patch('src.scraper.requests.get')
    def test_fetch_weather_timeout(self, mock_get):
        """Test handling of request timeout."""
        import requests
        mock_get.side_effect = requests.exceptions.Timeout()
        
        result = self.scraper.fetch_weather("Nabuti, Mukono, UG")
        
        self.assertIsNone(result)
    
    @patch('src.scraper.requests.get')
    def test_fetch_weather_http_error(self, mock_get):
        """Test handling of HTTP errors."""
        import requests
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        mock_get.return_value = mock_response
        
        result = self.scraper.fetch_weather("Invalid Location")
        
        self.assertIsNone(result)
    
    @patch('src.scraper.WeatherScraper.fetch_weather')
    def test_fetch_multiple_locations(self, mock_fetch):
        """Test fetching weather for multiple locations."""
        locations = [
            {"name": "Nabuti, Mukono, UG"},
            {"name": "Bugujju, Mukono, UG"}
        ]
        
        mock_fetch.side_effect = [
            {"location": "Nabuti", "temperature(C)": 25.0},
            {"location": "Bugujju", "temperature(C)": 24.5}
        ]
        
        results = self.scraper.fetch_multiple_locations(locations)
        
        self.assertEqual(len(results), 2)
        self.assertEqual(mock_fetch.call_count, 2)
    
    def test_init_without_api_key(self):
        """Test initialization without API key raises error."""
        with patch('src.scraper.API_KEY', None):
            with self.assertRaises(ValueError):
                WeatherScraper()


if __name__ == '__main__':
    unittest.main()
