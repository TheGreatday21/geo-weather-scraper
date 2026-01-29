"""
Storage module for saving and loading weather data.
"""
import os
import pandas as pd
import logging
from pathlib import Path
from typing import Optional
from .config import DATA_DIR, OUTPUT_FILENAME

logger = logging.getLogger(__name__)


class WeatherStorage:
    """Handles storage operations for weather data."""
    
    def __init__(self, data_dir: str = None, filename: str = None):
        """
        Initialize storage handler.
        
        Args:
            data_dir: Directory to store data files (defaults to config value)
            filename: Name of the output CSV file (defaults to config value)
        """
        self.data_dir = Path(data_dir or DATA_DIR)
        self.filename = filename or OUTPUT_FILENAME
        self.filepath = self.data_dir / self.filename
        
        # Create data directory if it doesn't exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def save_to_csv(self, df: pd.DataFrame, append: bool = True) -> bool:
        """
        Save DataFrame to CSV file.
        
        Args:
            df: DataFrame to save
            append: If True, append to existing file; if False, overwrite
            
        Returns:
            True if save was successful, False otherwise
        """
        if df.empty:
            logger.warning("Cannot save empty DataFrame")
            return False
        
        try:
            file_exists = self.filepath.exists()
            
            if append and file_exists:
                # Append mode: don't write header if file exists
                df.to_csv(
                    self.filepath,
                    mode='a',
                    header=False,
                    index=False
                )
                logger.info(f"Appended {len(df)} records to {self.filepath}")
            else:
                # Write mode: create new file or overwrite
                df.to_csv(
                    self.filepath,
                    mode='w',
                    header=True,
                    index=False
                )
                logger.info(f"Saved {len(df)} records to {self.filepath}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving data to CSV: {e}")
            return False
    
    def load_from_csv(self) -> Optional[pd.DataFrame]:
        """
        Load weather data from CSV file.
        
        Returns:
            DataFrame with weather data or None if file doesn't exist
        """
        if not self.filepath.exists():
            logger.warning(f"File not found: {self.filepath}")
            return None
        
        try:
            df = pd.read_csv(self.filepath)
            logger.info(f"Loaded {len(df)} records from {self.filepath}")
            return df
        except Exception as e:
            logger.error(f"Error loading data from CSV: {e}")
            return None
    
    def file_exists(self) -> bool:
        """
        Check if the data file exists.
        
        Returns:
            True if file exists, False otherwise
        """
        return self.filepath.exists()
    
    def get_filepath(self) -> Path:
        """
        Get the full filepath for the data file.
        
        Returns:
            Path object for the data file
        """
        return self.filepath
