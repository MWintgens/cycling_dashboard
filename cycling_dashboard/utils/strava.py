"""
Strava API utilities.

Vereiste env-variabelen (zet in .streamlit/secrets.toml):
    STRAVA_CLIENT_ID     = "12345"
    STRAVA_CLIENT_SECRET = "abc..."
    STRAVA_REFRESH_TOKEN = "def..."   ← genereer eenmalig via OAuth (zie README)

OAuth-flow voor de refresh token staat uitgelegd in README.md.
"""

import os
import time
import requests
import streamlit as st
from datetime import datetime
import math

# ── Token management ──────────────────────────────────────────────────────────

def _get_access_token() -> str:
    """Wissel refresh token in voor een geldig access token (automatisch vernieuwd)."""
    try:
        client_id     = st.secrets["STRAVA_CLIENT_ID"]
        client_secret = st.secrets["STRAVA_CLIENT_SECRET"]
        refresh_token = st.secrets["STRAVA_REFRESH_TOKEN"]
    except Exception:
        # Fallback naar env-vars (handig lokaal)
        client_id     = os.environ.get("STRAVA_CLIENT_ID", "")
        client_secret = os.environ.get("STRAVA_CLIENT_SECRET", "")
        refresh_token = os.environ.get("STRAVA_REFRESH_TOKEN", "")

    if not client_id:
        return ""  # Demo mode

    r = requests.post(
        "https://www.strava.com/oauth/token",
        data={
            "client_id":     client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
            "grant_type":    "refresh_token",
        },
        timeout=10,
    )
    r.raise_for_status()
    return r.json()["access_token"]


# ── Activities ────────────────────────────────────────────────────────────────

from datetime import datetime

def get_all_activities(max_pages: int = 20, start_date: str = "2026-01-01") -> list[dict]:
    token = _get_access_token()
    if not token:
        return _demo_activities()

    # Converteer startdatum naar Unix timestamp
    after = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp())

    activities = []
    for page in range(1, max_pages + 1):
        r = requests.get(
            "https://www.strava.com/api/v3/athlete/activities",
            headers={"Authorization": f"Bearer {token}"},
            params={"per_page": 100, "page": page, "after": after},  # ← after toevoegen
            timeout=15,
        )
        r.raise_for_status()
        batch = r.json()
        if not batch:
            break
        activities.extend(batch)

    activities = [a for a in activities if a.get("type") in ("Ride", "VirtualRide", "EBikeRide")]
    return activities


def get_latest_position(activities: list[dict]) -> dict | None:
    """Extraheer de laatste GPS-positie uit de meest recente activiteit."""
    for act in activities:
        end = act.get("end_latlng") or []
        start = act.get("start_latlng") or []
        coords = end or start
        if len(coords) == 2:
            return {
                "lat": coords[0],
                "lon": coords[1],
                "city": act.get("location_city") or act.get("location_country") or "onderweg",
                "activity_name": act.get("name", ""),
                "date": act.get("start_date_local", ""),
            }
    return None


# ── Demo data (als er geen Strava-koppeling is) ───────────────────────────────

def _demo_activities() -> list[dict]:
    """Realistische nep-activiteiten voor lokale demo zonder Strava."""
    import random
    random.seed(42)

    routes = [
        ("🏔️ Door de Alpen naar Innsbruck", 47.26, 11.39, 142, 2800),
        ("🌊 Langs de Donau richting Wenen", 48.20, 16.37, 98, 650),
        ("🌲 Zwarte Woud doorgetrokken", 48.00, 8.20, 115, 1900),
        ("🏙️ Door München naar de stad", 48.13, 11.57, 78, 420),
        ("🌾 Vlakke etappe richting Ulm", 48.39, 9.98, 110, 380),
        ("⛪ Langs het Bodenmeer", 47.66, 9.17, 88, 760),
        ("🇨🇭 Zwitserland binnenkomst!", 47.37, 8.54, 64, 1240),
        ("🗻 Grindelwald-klimmetje", 46.62, 8.03, 52, 3100),
    ]

    base = datetime(2025, 6, 1, 8, 0, 0)
    acts = []
    cumulative_days = 0
    for i, (name, lat, lon, dist, elev) in enumerate(routes):
        cumulative_days += random.randint(1, 3)
        dt = base + __import__("datetime").timedelta(days=cumulative_days)
        moving = int(dist / 18 * 3600)  # ~18 km/h gemiddeld
        acts.append({
            "id": 1000 + i,
            "name": name,
            "type": "Ride",
            "start_date_local": dt.isoformat(),
            "distance": dist * 1000,          # meters
            "total_elevation_gain": elev,
            "moving_time": moving,
            "elapsed_time": int(moving * 1.15),
            "start_latlng": [lat - 0.3, lon - 0.4],
            "end_latlng": [lat, lon],
            "map": {"summary_polyline": ""},   # leeg in demo
            "kudos_count": random.randint(3, 42),
            "location_city": name.split(" ")[-1],
            "location_country": "Germany" if lon < 12 else ("Switzerland" if lon < 9.5 else "Austria"),
        })
    return acts
