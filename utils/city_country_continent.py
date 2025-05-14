from geopy.geocoders import Nominatim
import pycountry
import pycountry_convert


def get_country_and_continent(city_name):
    geolocator = Nominatim(user_agent="amin.choudhury@prodinda.com")
    location = geolocator.geocode(city_name,  language="en")

    if not location:
        return None, None

    country_name = location.address.split(",")[-1].strip()

    try:
        country = pycountry.countries.lookup(country_name)
        country_code = country.alpha_2
        continent_code = pycountry_convert.country_alpha2_to_continent_code(country_code)
        continent_name = pycountry_convert.convert_continent_code_to_continent_name(continent_code)
        return country.name, continent_name
    except Exception as e:
        print(f"Error: {e}")
        return None, None
