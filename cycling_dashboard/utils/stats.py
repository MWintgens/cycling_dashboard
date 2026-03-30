"""
Statistieken-berekeningen: totalen + leuke vergelijkingen.
"""

from datetime import datetime
import math


# ── Totalen ───────────────────────────────────────────────────────────────────

COUNTRY_LOOKUP = {
    # Simpele heuristiek op basis van lon/lat bereiken — voor preciezere
    # detectie kun je de reverse-geocode van Open-Meteo of Nominatim gebruiken.
    "Germany":     (47.3, 55.1, 5.9, 15.0),
    "Austria":     (46.4, 49.0, 9.5, 17.2),
    "Switzerland": (45.8, 47.8, 5.9, 10.5),
    "France":      (41.3, 51.1, -5.2, 9.6),
    "Italy":       (35.5, 47.1, 6.6, 18.5),
    "Netherlands": (50.7, 53.6, 3.3, 7.2),
    "Belgium":     (49.5, 51.5, 2.5, 6.4),
    "Czech Republic": (48.5, 51.1, 12.1, 18.9),
    "Hungary":     (45.7, 48.6, 16.1, 22.9),
}


def _guess_country(lat, lon) -> str | None:
    for name, (lat_min, lat_max, lon_min, lon_max) in COUNTRY_LOOKUP.items():
        if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
            return name
    return None


def compute_totals(activities: list[dict]) -> dict:
    total_m   = sum(a.get("distance", 0) for a in activities)
    total_elev= sum(a.get("total_elevation_gain", 0) for a in activities)
    moving_s  = sum(a.get("moving_time", 0) for a in activities)
    n_rides   = len(activities)

    # Landen via Strava-veld of coördinaten
    countries = set()
    for a in activities:
        if a.get("location_country"):
            countries.add(a["location_country"])
        else:
            # Probeer via GPS
            for key in ("end_latlng", "start_latlng"):
                coords = a.get(key) or []
                if len(coords) == 2:
                    c = _guess_country(coords[0], coords[1])
                    if c:
                        countries.add(c)
                    break

    return {
        "distance_km":   total_m / 1000,
        "elevation_m":   total_elev,
        "rides":         n_rides,
        "moving_hours":  moving_s / 3600,
        "countries":     len(countries) if countries else max(1, n_rides // 3),
        "country_names": sorted(countries),
    }


# ── Fun stats ──────────────────────────────────────────────────────────────────

EIFFEL_HEIGHT_M   = 330      # meter
EVEREST_HEIGHT_M  = 8849
AMSTERDAM_MADRID  = 1771     # km
EARTH_CIRCUM_KM   = 40075
MARATHON_KM       = 42.195
WINDMILL_HEIGHT_M = 30       # typische Nederlandse molen


def compute_fun_stats(totals: dict) -> list[dict]:
    km    = totals["distance_km"]
    elev  = totals["elevation_m"]
    hours = totals["moving_hours"]
    rides = totals["rides"]

    stats = []

    # ── Afstand-vergelijkingen ────────────────────────────────────────────────
    pct_earth = (km / EARTH_CIRCUM_KM) * 100
    stats.append({
        "icon": "🌍",
        "text": f"<span class='fun-highlight'>{pct_earth:.1f}%</span> van de aardbol gefietst "
                f"({km:,.0f} van {EARTH_CIRCUM_KM:,} km)",
    })

    ams_mad = km / AMSTERDAM_MADRID
    if ams_mad >= 0.1:
        stats.append({
            "icon": "✈️",
            "text": f"Dat is <span class='fun-highlight'>{ams_mad:.1f}×</span> "
                    f"de afstand Amsterdam–Madrid",
        })

    marathons = km / MARATHON_KM
    stats.append({
        "icon": "🏃",
        "text": f"Gelijk aan <span class='fun-highlight'>{marathons:.0f} marathons</span> op de fiets",
    })

    # ── Hoogte-vergelijkingen ─────────────────────────────────────────────────
    eiffels = elev / EIFFEL_HEIGHT_M
    stats.append({
        "icon": "🗼",
        "text": f"<span class='fun-highlight'>{eiffels:.0f}× de Eiffeltoren</span> geklommen "
                f"({elev:,.0f} m totaal)",
    })

    everests = elev / EVEREST_HEIGHT_M
    if everests >= 0.5:
        stats.append({
            "icon": "🏔️",
            "text": f"<span class='fun-highlight'>{everests:.1f}× de Mount Everest</span> in hoogtemeters",
        })

    # ── Tijd ──────────────────────────────────────────────────────────────────
    if hours > 0:
        avg_speed = km / hours
        stats.append({
            "icon": "⚡",
            "text": f"Gemiddeld <span class='fun-highlight'>{avg_speed:.1f} km/h</span> — "
                    f"lekker op dreef!",
        })

    # ── Ritten ────────────────────────────────────────────────────────────────
    if rides > 0:
        avg_km = km / rides
        stats.append({
            "icon": "📅",
            "text": f"Gemiddeld <span class='fun-highlight'>{avg_km:.0f} km</span> per rit",
        })

    # ── Wielen omwentelingen (700c wiel, omtrek ≈ 2.1 m) ─────────────────────
    rotations = (km * 1000) / 2.1
    stats.append({
        "icon": "🔄",
        "text": f"De wielen draaiden <span class='fun-highlight'>{rotations:,.0f}×</span> rond",
    })

    return stats
