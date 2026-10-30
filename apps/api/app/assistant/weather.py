"""Open-Meteo current + short-range forecast (no API key). Cached ~10 minutes per rounded coordinate."""
from __future__ import annotations

import time

import httpx

_CACHE: dict[tuple[float, float], tuple[float, dict]] = {}
TTL = 600
CODES = {0: 'Clear', 1: 'Mostly clear', 2: 'Partly cloudy', 3: 'Overcast', 45: 'Fog', 48: 'Fog', 51: 'Light drizzle', 53: 'Drizzle',
         55: 'Heavy drizzle', 61: 'Light rain', 63: 'Rain', 65: 'Heavy rain', 71: 'Light snow', 73: 'Snow', 75: 'Heavy snow',
         80: 'Rain showers', 81: 'Rain showers', 82: 'Violent showers', 95: 'Thunderstorm', 96: 'Thunderstorm', 99: 'Thunderstorm'}


async def forecast(latitude: float, longitude: float, *, transport=None) -> dict:
    key = (round(latitude, 2), round(longitude, 2))
    hit = _CACHE.get(key)
    if hit and time.monotonic() - hit[0] < TTL:
        return hit[1]
    params = {'latitude': key[0], 'longitude': key[1], 'timezone': 'auto', 'forecast_hours': 6,
              'current': 'temperature_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m',
              'hourly': 'temperature_2m,precipitation_probability,weather_code'}
    async with httpx.AsyncClient(timeout=6, transport=transport) as client:
        response = await client.get('https://api.open-meteo.com/v1/forecast', params=params)
        response.raise_for_status()
        raw = response.json()
    cur, hourly = raw.get('current', {}), raw.get('hourly', {})
    result = {'source': 'Open-Meteo', 'latitude': key[0], 'longitude': key[1], 'timezone': raw.get('timezone'),
              'now': {'temperature_c': cur.get('temperature_2m'), 'feels_like_c': cur.get('apparent_temperature'),
                      'precipitation_mm': cur.get('precipitation'), 'wind_kmh': cur.get('wind_speed_10m'),
                      'summary': CODES.get(cur.get('weather_code'), 'Unknown')},
              'next_hours': [{'time': t, 'temperature_c': hourly['temperature_2m'][i],
                              'rain_chance_pct': (hourly.get('precipitation_probability') or [None] * 99)[i],
                              'summary': CODES.get(hourly['weather_code'][i], 'Unknown')}
                             for i, t in enumerate(hourly.get('time', [])[:6])]}
    _CACHE[key] = (time.monotonic(), result)
    return result
