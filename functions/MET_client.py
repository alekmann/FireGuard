import requests

headers = {
    "User-Agent": "FireGuard/1.0.0 (598118@stud.hvl.no)"
}


def fetch_weather(lat, lon):
    r = requests.get(f"https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={lat}&lon={lon}", headers=headers)
    if r.status_code == 200:
        data = r.json()
        return data
    else:
        print(f"Error fetching weather data: {r.status_code}")
        return None

def extract_timeseries(raw_json):
    return raw_json['properties']['timeseries']

def get_air_temperature(ts):
    return ts["data"]["instant"]["details"]["air_temperature"]

def get_wind_speed(ts):
    return ts["data"]["instant"]["details"]["wind_speed"]

def get_relative_humidity(ts):
    return ts["data"]["instant"]["details"]["relative_humidity"]

def get_precipitation_next_hour(ts):
    '''Returns the precipitation amount for the next hour in mm.'''
    return ts["data"]["next_1_hours"]["details"]["precipitation_amount"]

def extract_weather_data(raw_json):

    ts0 = extract_timeseries(raw_json)[0]

    temp = get_air_temperature(ts0)
    wind = get_wind_speed(ts0)
    hum = get_relative_humidity(ts0)
    precip = get_precipitation_next_hour(ts0)

    return {
        "temperature": temp,
        "wind_speed": wind,
        "relative_humidity": hum,
        "precipitation_next_hour": precip
    }

raw_data = fetch_weather(60.3913, 5.3221)

weather = extract_weather_data(raw_data)

print(weather)


   
