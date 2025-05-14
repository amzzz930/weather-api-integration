import requests
import logging
from datetime import datetime, timedelta

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
            "created_at": get_datetime_now_rounded(),
        }
        return weather_info

    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {e}")
        return {"error": f"Request failed: {e}"}
    except (KeyError, IndexError, TypeError) as e:
        logging.error(f"Error processing data: {e}")
        return {"error": f"Error processing data: {e}"}

def get_datetime_now_rounded() -> str:
    """Returns the current timestamp rounded up to the next second in ISO format."""
    now = datetime.now()
    rounded_up = now + timedelta(seconds=1) if now.microsecond > 0 else now
    return rounded_up.replace(microsecond=0).isoformat()