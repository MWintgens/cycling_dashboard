"""
Activiteiten-feed: bouw een tijdlijn van recente ritten.
"""

from datetime import datetime


def build_feed(activities: list[dict], n: int = 10) -> list[dict]:
    """Maak een lijst van de n meest recente ritten, geformatteerd voor weergave."""
    # Sorteer op startdatum (meest recent eerst). Strava-activiteiten kunnen
    # in willekeurige volgorde binnenkomen, dus expliciet sorteren is veiliger.
    def _parse_dt(a):
        s = a.get("start_date_local") or ""
        try:
            return datetime.fromisoformat(s)
        except Exception:
            return datetime.min

    sorted_acts = sorted(activities, key=_parse_dt, reverse=True)

    result = []
    for act in sorted_acts[:n]:
        dt_str = act.get("start_date_local", "")
        try:
            dt = datetime.fromisoformat(dt_str)
            # Gebruik locale-onafhankelijke formatting: dag, korte maand, jaar
            date_str = f"{dt.day} {dt.strftime('%b')} {dt.year}"
        except Exception:
            date_str = dt_str[:10] if dt_str else "?"

        moving_s = act.get("moving_time", 0)
        hours    = moving_s // 3600
        minutes  = (moving_s % 3600) // 60
        duration = f"{hours}u{minutes:02d}" if hours else f"{minutes}min"

        result.append({
            "date":      date_str,
            "name":      act.get("name", "Naamloze rit"),
            "distance":  act.get("distance", 0) / 1000,
            "elevation": act.get("total_elevation_gain", 0),
            "duration":  duration,
            "kudos":     act.get("kudos_count", 0),
        })
    return result
