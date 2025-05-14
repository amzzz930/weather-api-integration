from datetime import datetime, timedelta
import logging
import traceback

from helpers.postgres.driver import PostgresDriver
from utils.weather_api import get_weather
from utils.weather_integration.constants import tables
from utils.city_country_continent import get_country_and_continent

KELVIN_TO_CELSIUS = 273.15

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Transform:
    def __init__(self):
        self.postgres = PostgresDriver()

    def create_tables(self):
        """ create tables in the PostgreSQL database """
        for table_name in tables:
            self.postgres.create_table(table_name, tables[table_name])

    def push_to_postgres_weather_data(self, city_name: str):
        """Fetches and inserts weather data for a city into the weather_data table."""
        try:
            weather_info = get_weather(city_name)
            required_keys = ["city", "main", "description", "temperature", "created_at"]
            missing_keys = [key for key in required_keys if key not in weather_info]

            if missing_keys:
                logger.error(f"❌ Missing keys in weather data: {missing_keys}")
                return

            query = """
                INSERT INTO weather_data (city, main, description, temperature, created_at)
                VALUES (%s, %s, %s, %s, %s)
            """
            values = (
                weather_info["city"],
                weather_info["main"],
                weather_info["description"],
                weather_info["temperature"],
                weather_info["created_at"],
            )

            self.postgres.put_query(query, values)
            logger.info(f"✅ Successfully inserted weather data for {weather_info['city']}")

        except Exception as e:
            logger.error(f"❌ Failed to insert weather data for {city_name}: {type(e).__name__}: {e}")
            logger.debug(traceback.format_exc())

    def push_to_postgres_country_continent(self, city_name: str):
        """Fetches and inserts country and continent info for a city into the city_country_continent table."""
        try:
            country, continent = get_country_and_continent(city_name)

            if not country or not continent:
                logger.warning(f"⚠️ Could not resolve country or continent for city: {city_name}")
                return

            query = """
                INSERT INTO city_country_continent (city, country, continent)
                VALUES (%s, %s, %s)
            """
            values = (city_name, country, continent)

            self.postgres.put_query(query, values)
            logger.info(f"✅ Successfully inserted location data for {city_name}")

            self.postgres.remove_duplicates("city_country_continent", ["city"])

        except Exception as e:
            logger.error(f"❌ Failed to insert location data for {city_name}: {type(e).__name__}: {e}")
            logger.debug(traceback.format_exc())