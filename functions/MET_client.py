import requests

headers = {
    "User-Agent": "FireGuard/1.0.0 (598118@stud.hvl.no)"
}


def fetch_weather(lat: float, lon: float) -> dict:
    url = f"https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={lat}&lon={lon}"
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise RuntimeError(f"Failed to fetch weather data from MET: {exc}") from exc
    return response.json()


def extract_timeseries(raw_json: dict) -> list[dict]:
    try:
        return raw_json["properties"]["timeseries"]
    except (KeyError, TypeError) as exc:
        raise ValueError("Unexpected MET response format") from exc


def get_air_temperature(ts: dict) -> float:
    return ts["data"]["instant"]["details"]["air_temperature"]


def get_wind_speed(ts: dict) -> float:
    return ts["data"]["instant"]["details"]["wind_speed"]


def get_relative_humidity(ts: dict) -> float:
    return ts["data"]["instant"]["details"]["relative_humidity"]


def _to_record(ts: dict) -> dict:
    return {
        "timestamp": ts["time"],
        "temperature": float(get_air_temperature(ts)),
        "wind_speed": float(get_wind_speed(ts)),
        "relative_humidity": float(get_relative_humidity(ts)),
    }


def extract_weather_records(raw_json: dict, max_points: int = 12) -> list[dict]:
    if max_points < 1:
        raise ValueError("max_points must be >= 1")

    records: list[dict] = []
    for ts in extract_timeseries(raw_json):
        try:
            records.append(_to_record(ts))
        except (KeyError, TypeError, ValueError):
            continue
        if len(records) >= max_points:
            break

    if not records:
        raise ValueError("No valid weather records found in MET response")

    return records


def fetch_weather_records_for_location(lat: float, lon: float, max_points: int = 12) -> list[dict]:
    raw_data = fetch_weather(lat=lat, lon=lon)
    return extract_weather_records(raw_data, max_points=max_points)



