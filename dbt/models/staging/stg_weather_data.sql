SELECT
    *
FROM {{ source('weather_data_sources', 'weather_data') }}
