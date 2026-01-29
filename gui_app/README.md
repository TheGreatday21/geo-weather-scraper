# Weather Data app for mac

This is a **separate GUI application** for the weather  application. 

It provides a desktop interface to:
- Set your OpenWeather API key (saved into the pipeline’s `.env`)
- Configure the number of iterations + delay of iterations 
- You can easily edit the list of locations
- Start/Stop the collection loop
- View logs live

## Requirements

- macOS with Python 3 installed
- The main pipeline directory must exist next to this folder (this repo already has it)

## Run the GUI

From the project root:

```bash
cd "/Users/user_name/WEATHER_SCRAPPING_TOOL/gui_app"
python3 src/app.py
```

## Notes

- This GUI imports and reuses the pipeline code from `../src/` (so you only maintain one scraper).
- Output CSV is still written by the pipeline into `../data/` (same as CLI mode).

