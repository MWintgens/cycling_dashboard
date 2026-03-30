"""
Activiteiten-feed: bouw een tijdlijn van recente ritten.
"""

from datetime import datetime


def build_feed(activities: list[dict], n: int = 10) -> list[dict]:
    """Maak een lijst van de n meest recente ritten, geformatteerd voor weergave."""
    result = []
    for act in activities[:n]:
        dt_str = act.get("start_date_local", "")
        try:
            dt = datetime.fromisoformat(dt_str)
            date_str = dt.strftime("%-d %b %Y")  # bijv. "7 jun 2025"
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
