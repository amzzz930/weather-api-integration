SELECT
    *
FROM {{ source('weather_data_sources', 'city_country_continent') }}