"""
Main entry point for weather data pipeline.
"""
import logging
import time
import sys
from src.scraper import WeatherScraper
from src.parser import WeatherParser
from src.storage import WeatherStorage
from src.config import (
    DEFAULT_LOCATIONS,
    SCRAPE_DELAY_SECONDS,
    NUM_ITERATIONS,
    LOG_LEVEL,
    LOG_FORMAT
)

# Configure logging
logging.basicConfig(
    level=LOG_LEVEL,
    format=LOG_FORMAT,
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Main function to orchestrate weather data collection."""
    logger.info("Starting weather data pipeline...")
    
    # Initialize components
    scraper = WeatherScraper()
    parser = WeatherParser()
    storage = WeatherStorage()
    
    # Collect weather data over multiple iterations
    all_weather_data = []
    
    try:
        for iteration in range(NUM_ITERATIONS):
            logger.info(f"Reading {iteration + 1} of {NUM_ITERATIONS}")
            
            # Fetch weather data for all locations
            iteration_data = scraper.fetch_multiple_locations(DEFAULT_LOCATIONS)
            
            if iteration_data:
                all_weather_data.extend(iteration_data)
                logger.info(f"Collected {len(iteration_data)} records in this iteration")
            else:
                logger.warning("No data collected in this iteration")
            
            # Wait before next iteration (except for the last one)
            if iteration < NUM_ITERATIONS - 1:
                logger.info(f"Waiting {SCRAPE_DELAY_SECONDS // 60} minutes before next reading...")
                time.sleep(SCRAPE_DELAY_SECONDS)
        
        # Process and save data
        if not all_weather_data:
            logger.error("No weather data has been collected")
            return
        
        # Validate data
        if not parser.validate_data(all_weather_data):
            logger.error("Data validation failed")
            return
        
        # Convert to DataFrame
        df = parser.to_dataframe(all_weather_data)
        
        # Save to CSV
        if storage.save_to_csv(df, append=True):
            logger.info(f"Successfully saved {len(df)} records to {storage.get_filepath()}")
            
            # Display summary statistics
            stats = parser.get_summary_stats(df)
            logger.info(f"Summary: {stats}")
        else:
            logger.error("Failed to save data to CSV")
            return
        
        logger.info("Weather data pipeline completed successfully")
        
    except KeyboardInterrupt:
        logger.info("Pipeline interrupted by user")
        # Save any collected data before exiting
        if all_weather_data:
            logger.info("Saving collected data before exit...")
            df = parser.to_dataframe(all_weather_data)
            storage.save_to_csv(df, append=True)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
