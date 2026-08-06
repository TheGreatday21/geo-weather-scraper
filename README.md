#GITHUB LINK TO PROJECT : https://github.com/TheGreatday21/geo-weather-scraper 


# Geo-weather-scraper

Geo weather is an open-source python tool for scraping and storing weather data from the OpenWeatherMap API. This tool helps collect weather information for multiple locations over time, enabling better weather prediction and decision-making.

## Features

It has the capability to collect weather data from multiple location simultaneously, do the scraping automatically at intervals, store this collected data and use jupyter notebooks for exploratory data analysis to pick insights .


## Project Structure

```
weather-data-pipeline/
│
├── src/
│   ├── __init__.py
│   ├── scraper.py      # Weather API scraping logic
│   ├── parser.py        # Data parsing and transformation
│   ├── storage.py       # CSV file operations
│   └── config.py        # Configuration management
│
├── data/
│   └── samples/         # Sample data directory
│
├── notebooks/
│   └── exploration.ipynb  # Data exploration notebook
│
├── tests/
│   ├── __init__.py
│   └── test_scraper.py    # Unit tests
│
├── .gitignore
├── .env.example          # Environment variables template
├── requirements.txt      # Python dependencies
├── README.md
└── main.py              # Main entry point
```

## Installation

1. **Clone the repository** (if applicable) or navigate to the project directory:
   ```bash
   cd WEATHER_SCRAPPING_TOOL
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your OpenWeatherMap API key:
   ```
   OPENWEATHER_API_KEY=your_api_key_here
   ```

## Usage

### Basic Usage

Run the main script to start collecting weather data:

```bash
python main.py
```

This will:
- Collect weather data for all configured locations
- Run for the specified number of iterations (default: 10)
- Wait between iterations (default: 3 minutes)
- Save all data to `data/weather_data.csv`

### Configuration

Edit `.env` file to customize behavior:

```env
# API Configuration
OPENWEATHER_API_KEY=your_api_key_here
OPENWEATHER_BASE_URL=https://api.openweathermap.org/data/2.5/weather
REQUEST_TIMEOUT=10

# Scraping Configuration
SCRAPE_DELAY_MINUTES=3      # Minutes between iterations
NUM_ITERATIONS=10            # Number of data collection cycles

# Data Storage
OUTPUT_FILENAME=weather_data.csv

# Logging
LOG_LEVEL=INFO              # DEBUG, INFO, WARNING, ERROR
```

### Programmatic Usage

You can also use the modules programmatically:

```python
from src.scraper import WeatherScraper
from src.parser import WeatherParser
from src.storage import WeatherStorage

# Initialize components
scraper = WeatherScraper()
parser = WeatherParser()
storage = WeatherStorage()

# Fetch weather data
locations = [{"name": "Nabuti, Mukono, UG"}]
data = scraper.fetch_multiple_locations(locations)

# Convert to DataFrame
df = parser.to_dataframe(data)

# Save to CSV
storage.save_to_csv(df)
```

## Data Exploration

Use the provided Jupyter notebook to explore and visualize collected data:

```bash
jupyter notebook notebooks/exploration.ipynb
```

The notebook includes:
- Data loading and inspection
- Summary statistics
- Temperature trend visualization
- Location-based filtering
- Distribution analysis

## Testing

Run the test suite:

```bash
python -m pytest tests/
```

Or run specific tests:

```bash
python -m pytest tests/test_scraper.py -v
```

## Data Format

The collected weather data includes:

- `timestamp`: Date and time of collection (EAT timezone)
- `location`: Location name
- `weather`: Weather description
- `temperature(C)`: Temperature in Celsius
- `wind_speed(mps)`: Wind speed in meters per second
- `humidity(%)`: Humidity percentage
- `pressure(hPa)`: Atmospheric pressure
- `feels_like(C)`: Feels-like temperature
- `visibility(m)`: Visibility in meters
- `clouds(%)`: Cloud coverage percentage

## Default Locations

The tool is configured to collect data for these locations in Mukono, Uganda:

- Nabuti, Mukono, UG
- Bugujju, Mukono, UG
- Seeta, Mukono, UG
- Namilyango, Mukono, UG
- Kyetume, Mukono, UG

You can modify the `DEFAULT_LOCATIONS` list in `src/config.py` to change these.

## Error Handling

The tool includes comprehensive error handling:

- **API errors**: Handles timeouts, HTTP errors, and invalid responses
- **Data validation**: Validates data structure before saving
- **File operations**: Handles file I/O errors gracefully
- **Logging**: All errors are logged with detailed information

## Logging

Logs are output to stdout with timestamps and log levels. Set `LOG_LEVEL` in `.env` to control verbosity:

- `DEBUG`: Detailed debugging information
- `INFO`: General informational messages (default)
- `WARNING`: Warning messages
- `ERROR`: Error messages only

## Requirements

- Python 3.8+
- requests
- pandas
- python-dotenv

See `requirements.txt` for specific versions.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

See LICENSE file for details.

## Troubleshooting

### API Key Issues
- Ensure your API key is correctly set in `.env`
- Verify the API key is active on OpenWeatherMap
- Check for any API rate limits

### Data Not Saving
- Check file permissions in the `data/` directory
- Ensure the directory exists (it will be created automatically)
- Check logs for specific error messages

### Import Errors
- Ensure you're running from the project root directory
- Verify all dependencies are installed: `pip install -r requirements.txt`
- Check that virtual environment is activated

## Future Enhancements

- [ ] Database storage option (PostgreSQL, SQLite)
- [ ] Real-time data visualization dashboard
- [ ] Email/SMS alerts for weather conditions
- [ ] Historical data analysis
- [ ] Weather prediction models
- [ ] Docker containerization
- [ ] Scheduled task support (cron, Celery)

## Support

For issues, questions, or contributions, please open an issue on the repository.
