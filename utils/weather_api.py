import requests
from datetime import datetime


def weather(city_name: str):
   
    #URL and API key 
    url='https://api.openweathermap.org/data/2.5/weather?'
    API_key='c4cd0778e6cbc97263e6774108de2adf'
    
    #Get response from weather API 
    params = {'q': city_name, 'appid': API_key}
    response = requests.get(url, params=params)
    result=response.json()
    
    #Convert temperature to °C 
    temp=round(result.get("main").get("temp")- 273.15)
    temp=f'{temp}°C'

    #Create dictionary with city weather information 
    weather_info={
     'city': result.get("name"), 
     'country': result.get("sys").get("country"),
     'main': result.get("weather")[0].get("main"),
     'description':result.get("weather")[0].get("description"),
     'temperature':temp,
     'current_time': datetime.today().strftime('%Y-%m-%d %H:%M:%S')
     }
    
    return weather_info 
