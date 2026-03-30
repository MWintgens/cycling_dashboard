"""
Interactieve kaart via Folium.
Toont alle Strava-routes + huidige positie-marker.
"""

import folium
from folium import plugins
import polyline  # pip install polyline


def render_map(activities: list[dict], latest_pos: dict | None) -> str:
    """Genereer een Folium-kaart als HTML string."""

    # Bepaal startpunt van kaart
    if latest_pos:
        center = [latest_pos["lat"], latest_pos["lon"]]
    elif activities:
        first = activities[-1]  # oudste rit
        coords = first.get("start_latlng") or [50.0, 10.0]
        center = coords
    else:
        center = [50.0, 10.0]

    m = folium.Map(
        location=center,
        zoom_start=6,
        tiles="CartoDB Positron",
        control_scale=True,
    )

    # ── Routes tekenen ────────────────────────────────────────────────────────
    route_points_all = []  # voor automatisch zoomen

    for i, act in enumerate(reversed(activities)):  # oud → nieuw
        poly = act.get("map", {}).get("summary_polyline", "")
        if poly:
            try:
                decoded = polyline.decode(poly)
                route_points_all.extend(decoded)
                # Oudere ritten = lichter grijs, recente = oranje
                age_frac = i / max(len(activities) - 1, 1)
                color = _interpolate_color(age_frac)
                folium.PolyLine(
                    decoded,
                    color=color,
                    weight=3,
                    opacity=0.7,
                    tooltip=f"🚴 {act.get('name','Rit')} — {act.get('distance',0)/1000:.1f} km",
                ).add_to(m)
            except Exception:
                pass
        else:
            # Geen polyline: teken rechte lijn van start → eind
            start = act.get("start_latlng") or []
            end   = act.get("end_latlng") or []
            if len(start) == 2 and len(end) == 2:
                age_frac = i / max(len(activities) - 1, 1)
                color = _interpolate_color(age_frac)
                pts = [start, end]
                route_points_all.extend(pts)
                folium.PolyLine(
                    pts,
                    color=color,
                    weight=3,
                    opacity=0.6,
                    dash_array="8 4",
                    tooltip=f"🚴 {act.get('name','Rit')} — {act.get('distance',0)/1000:.1f} km",
                ).add_to(m)
            elif len(start) == 2:
                route_points_all.append(start)

    # ── Huidige positie marker ────────────────────────────────────────────────
    if latest_pos:
        folium.Marker(
            location=[latest_pos["lat"], latest_pos["lon"]],
            popup=folium.Popup(
                f"<b>📍 Roos is hier!</b><br>"
                f"{latest_pos.get('city','')}<br>"
                f"<small>{latest_pos.get('activity_name','')}</small>",
                max_width=200,
            ),
            icon=folium.CustomIcon(
                icon_image="https://cdn-icons-png.flaticon.com/32/3163/3163059.png",
                icon_size=(32, 32),
            ),
            tooltip="📍 Roos is hier!",
        ).add_to(m)

        # Puls-cirkel rondom huidige positie
        folium.CircleMarker(
            location=[latest_pos["lat"], latest_pos["lon"]],
            radius=14,
            color="#ff6b35",
            fill=True,
            fill_color="#ff6b35",
            fill_opacity=0.2,
            weight=2,
        ).add_to(m)

    # ── Startpunt markeren ────────────────────────────────────────────────────
    if activities:
        start_act = activities[-1]
        start_coords = start_act.get("start_latlng") or []
        if len(start_coords) == 2:
            folium.Marker(
                location=start_coords,
                icon=folium.Icon(color="green", icon="home", prefix="fa"),
                tooltip="🏠 Startpunt",
            ).add_to(m)

    # ── Zoom op route ─────────────────────────────────────────────────────────
    if route_points_all:
        lats = [p[0] for p in route_points_all]
        lons = [p[1] for p in route_points_all]
        m.fit_bounds([[min(lats), min(lons)], [max(lats), max(lons)]])

    return m._repr_html_()


def _interpolate_color(frac: float) -> str:
    """Interpoleer van grijs (oud) naar oranje (recent)."""
    # frac 0 = oud, 1 = nieuw
    r = int(180 + frac * (255 - 180))
    g = int(180 - frac * (180 - 107))
    b = int(180 - frac * 127)
    return f"#{r:02x}{g:02x}{b:02x}"
