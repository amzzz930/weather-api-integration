-- dbt/models/final/final_table.sql
SELECT
    wd.*,
    cc.country,
    cc.continent
FROM {{ ref('stg_weather_data') }} AS wd
JOIN {{ ref('stg_city_country_continent') }} AS cc
  ON LOWER(wd.city) = LOWER(cc.city)
