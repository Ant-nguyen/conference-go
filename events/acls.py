from events.keys import PEXELS_API_KEY,OPEN_WEATHER_API_KEY
import requests
import json

def get_location_pexelapi(city):
    city= city.replace(" ","%20")
    pexelquery= f"https://api.pexels.com/v1/search?query={city}&per_page=1"
    header= {"Authorization":PEXELS_API_KEY}
    response = requests.get(pexelquery,headers=header)
    content = json.loads(response.content)
    try:
        photo = content["photos"][0]["url"]
    except:
        photo = None
    result ={"picture_url": photo
    }
    return result



def get_weather(city):
    city= city.replace(" ","%20")
    location_query = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={OPEN_WEATHER_API_KEY}"
    response = requests.get(location_query)
    content = json.loads(response.content)
    try:
        lat,lon = content[0]["lat"],content[0]["lon"]
    except:
        lat,lon = None,None

    weather_query = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPEN_WEATHER_API_KEY}"
    weather_response = requests.get(weather_query)
    weather_content= json.loads(weather_response.content)
    if "weather" in weather_content:
        weather = weather_content.get("weather")[0].get("description")
        temp = weather_content.get("main").get("temp")
    else:
        return None
    return {"temp":temp ,"description":weather}
