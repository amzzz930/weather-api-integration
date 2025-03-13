import requests
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# URL and API key
URL = "https://api.openweathermap.org/data/2.5/weather"
API_KEY = "c4cd0778e6cbc97263e6774108de2adf"

def get_weather(city_name: str) -> dict:
    """
    Fetches weather information for a given city using OpenWeatherMap API.

    Args:
        city_name (str): Name of the city.

    Returns:
        dict: Dictionary containing weather details or an error message.
    """
    params = {"q": city_name, "appid": API_KEY, "units": "metric"}  # Units set to metric for °C
    try:
        logging.info(f"Fetching weather data for city: {city_name}")
        response = requests.get(URL, params=params)
        response.raise_for_status()  # Raise an error for HTTP issues
        data = response.json()
        logging.info(f"Successfully retrieved weather data for {city_name}")

        # Extract weather information
        weather_info = {
            "city": data.get("name"),
            "country": data.get("sys", {}).get("country"),
            "main": data.get("weather", [{}])[0].get("main"),
            "description": data.get("weather", [{}])[0].get("description"),
            "temperature": round(data.get("main", {}).get("temp", 0)),  # Default to 0 if key is missing
            "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        return weather_info

    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {e}")
        return {"error": f"Request failed: {e}"}
    except (KeyError, IndexError, TypeError) as e:
        logging.error(f"Error processing data: {e}")
        return {"error": f"Error processing data: {e}"}