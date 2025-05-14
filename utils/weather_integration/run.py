import logging
from utils.weather_integration.transform import Transform

CITIES = ["london", "paris", "berlin", "sylhet"]

logger = logging.getLogger(__name__)


class Run:
    @classmethod
    def run_integration(cls):
        transform = Transform()
        transform.create_tables()

        for city in CITIES:
            logger.info(f"Attempting to fetch and push data for {city}")
            try:
                transform.push_to_postgres_weather_data(city)
                logger.info(f"Successfully pushed weather data for {city}\n")
            except Exception as e:
                logger.error(f"Failed to fetch or push weather data for {city}: {e}\n")
            try:
                transform.push_to_postgres_country_continent(city)
                logger.info(f"Successfully pushed country continent data for {city}\n")
            except Exception as e:
                logger.error(f"Failed to fetch or push country continent data for {city}: {e}\n")
