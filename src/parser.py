"""
Data parsing and transformation module for weather data.
"""
import pandas as pd
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class WeatherParser:
    """Handles parsing and transformation of weather data."""
    
    @staticmethod
    def to_dataframe(weather_data: List[Dict]) -> pd.DataFrame:
        """
        Convert list of weather data dictionaries to pandas DataFrame.
        
        Args:
            weather_data: List of weather data dictionaries
            
        Returns:
            pandas DataFrame with weather data
        """
        if not weather_data:
            logger.warning("No weather data provided, returning empty DataFrame")
            return pd.DataFrame()
        
        try:
            df = pd.DataFrame(weather_data)
            logger.info(f"Successfully converted {len(weather_data)} records to DataFrame")
            return df
        except Exception as e:
            logger.error(f"Error converting weather data to DataFrame: {e}")
            raise
    
    @staticmethod
    def validate_data(weather_data: List[Dict]) -> bool:
        """
        Validate weather data structure.
        
        Args:
            weather_data: List of weather data dictionaries
            
        Returns:
            True if data is valid, False otherwise
        """
        if not weather_data:
            return False
        
        required_fields = ["timestamp", "location", "temperature(C)"]
        
        for record in weather_data:
            if not isinstance(record, dict):
                logger.error(f"Invalid record type: {type(record)}")
                return False
            
            for field in required_fields:
                if field not in record:
                    logger.error(f"Missing required field: {field}")
                    return False
        
        return True
    
    @staticmethod
    def filter_by_location(df: pd.DataFrame, location: str) -> pd.DataFrame:
        """
        Filter DataFrame by location name.
        
        Args:
            df: DataFrame containing weather data
            location: Location name to filter by
            
        Returns:
            Filtered DataFrame
        """
        if df.empty:
            return df
        
        return df[df["location"] == location]
    
    @staticmethod
    def get_summary_stats(df: pd.DataFrame) -> Dict:
        """
        Get summary statistics for weather data.
        
        Args:
            df: DataFrame containing weather data
            
        Returns:
            Dictionary with summary statistics
        """
        if df.empty:
            return {}
        
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
        
        stats = {
            "total_records": len(df),
            "unique_locations": df["location"].nunique() if "location" in df.columns else 0,
            "date_range": {
                "start": df["timestamp"].min() if "timestamp" in df.columns else None,
                "end": df["timestamp"].max() if "timestamp" in df.columns else None,
            }
        }
        
        if "temperature(C)" in df.columns:
            stats["temperature"] = {
                "mean": df["temperature(C)"].mean(),
                "min": df["temperature(C)"].min(),
                "max": df["temperature(C)"].max(),
            }
        
        return stats
