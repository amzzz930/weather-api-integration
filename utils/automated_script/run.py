# Handle imports differently when run as a script vs module
import pandas as pd
import os
import sys

# Add the project root directory to the Python path
# This helps when running the script directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

try:
    # When imported as a module from the main package
    from utils.automated_script.get import WeatherAPI
except ModuleNotFoundError:
    # When run directly as a script
    from utils.automated_script.get import WeatherAPI

# URL and API key
URL = "https://api.openweathermap.org/data/2.5/weather"
API_KEY = "c4cd0778e6cbc97263e6774108de2adf"
CITY_NAMES = ["london", "sylhet", "paris", "tokyo", "madrid"]


def run():
    w_api = WeatherAPI(url=URL, api_key=API_KEY)

    city_data = []

    for city in CITY_NAMES:
        data = w_api.get_weather(city)
        city_data.append(data)

    df = pd.DataFrame(city_data)

    # Save dataframe as CSV
    csv_path = "weather_data.csv"
    df.to_csv(csv_path, index=False)

    print(f"Weather data saved to {csv_path}")
    return df, csv_path


# Make the script executable from command line
if __name__ == "__main__":
    run()
