"""
Weer via Open-Meteo — volledig gratis, geen API-key nodig.
Geeft huidige dag + 7-daagse voorspelling.
"""

import requests
from datetime import datetime, timedelta
import streamlit as st

WMO_ICONS = {
    0: ("☀️", "Helder"),
    1: ("🌤️", "Overwegend helder"),
    2: ("⛅", "Gedeeltelijk bewolkt"),
    3: ("☁️", "Bewolkt"),
    45: ("🌫️", "Mist"),
    48: ("🌫️", "IJsmist"),
    51: ("🌦️", "Lichte motregen"),
    53: ("🌦️", "Motregen"),
    55: ("🌧️", "Zware motregen"),
    61: ("🌧️", "Lichte regen"),
    63: ("🌧️", "Regen"),
    65: ("🌧️", "Zware regen"),
    71: ("🌨️", "Lichte sneeuw"),
    73: ("❄️", "Sneeuw"),
    75: ("❄️", "Zware sneeuw"),
    80: ("🌦️", "Regenbuien"),
    81: ("🌧️", "Zware buien"),
    82: ("⛈️", "Zeer zware buien"),
    95: ("⛈️", "Onweer"),
    99: ("⛈️", "Onweer met hagel"),
}

DAY_NAMES_NL = ["ma", "di", "wo", "do", "vr", "za", "zo"]


@st.cache_data(ttl=1800, show_spinner=False)
def get_weather(lat: float, lon: float) -> dict | None:
    """Haal weer op voor de opgegeven coördinaten."""
    try:
        r = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "current": [
                    "temperature_2m",
                    "weathercode",
                    "windspeed_10m",
                    "precipitation",
                ],
                "daily": [
                    "weathercode",
                    "temperature_2m_max",
                    "temperature_2m_min",
                    "precipitation_sum",
                    "windspeed_10m_max",
                ],
                "timezone": "auto",
                "forecast_days": 8,
                "wind_speed_unit": "kmh",
            },
            timeout=10,
        )
        r.raise_for_status()
        data = r.json()
    except Exception:
        return None

    daily = data.get("daily", {})
    dates = daily.get("time", [])
    codes = daily.get("weathercode", [])
    t_max = daily.get("temperature_2m_max", [])
    t_min = daily.get("temperature_2m_min", [])
    precip = daily.get("precipitation_sum", [])
    wind   = daily.get("windspeed_10m_max", [])

    # Vandaag
    today_code = codes[0] if codes else 0
    icon, description = WMO_ICONS.get(today_code, ("🌡️", "Onbekend"))
    today_weather = {
        "icon": icon,
        "description": description,
        "temp_max": t_max[0] if t_max else 0,
        "temp_min": t_min[0] if t_min else 0,
        "precip": precip[0] if precip else 0,
        "wind": wind[0] if wind else 0,
    }

    # 7-daagse voorspelling (sla vandaag over → start bij index 1)
    forecast = []
    for i in range(1, min(8, len(dates))):
        code = codes[i] if i < len(codes) else 0
        f_icon, _ = WMO_ICONS.get(code, ("🌡️", ""))
        date_obj = datetime.fromisoformat(dates[i])
        forecast.append({
            "day": DAY_NAMES_NL[date_obj.weekday()],
            "icon": f_icon,
            "temp_max": t_max[i] if i < len(t_max) else 0,
            "temp_min": t_min[i] if i < len(t_min) else 0,
            "precip": precip[i] if i < len(precip) else 0,
        })

    return {"today": today_weather, "forecast": forecast}
