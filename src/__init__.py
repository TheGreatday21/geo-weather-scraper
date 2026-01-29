"""
This is to acquire the main modules of the Weather Scraping Tool package.
"""
from .scraper import WeatherScraper
from .parser import WeatherParser
from .storage import WeatherStorage

__all__ = ['WeatherScraper', 'WeatherParser', 'WeatherStorage']
