import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import time

from utils.strava import get_all_activities, get_latest_position
from utils.weather import get_weather
from utils.stats import compute_fun_stats, compute_totals
from utils.map import render_map
from utils.feed import build_feed

st.set_page_config(
    page_title="🚴 Roos's Fietsavontuur",
    page_icon="🚴",
    layout="wide",
    initial_sidebar_state="collapsed",
)



# ── Styling ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background: #f7f4ef; }
    .metric-card {
        background: white;
        border-radius: 14px;
        padding: 1.1rem 1.4rem;
        box-shadow: 0 1px 6px rgba(0,0,0,.06);
        margin-bottom: .8rem;
    }
    .metric-val { font-size: 2rem; font-weight: 700; color: #1a1a1a; line-height: 1.1; }
    .metric-label { font-size: .8rem; color: #888; margin-top: .15rem; }
    .update-pill {
        display: inline-block;
        background: #e8f5e9;
        color: #2e7d32;
        border-radius: 999px;
        padding: .15rem .7rem;
        font-size: .75rem;
        font-weight: 600;
    }
    h1 { font-size: 1.8rem !important; }
    .section-title { font-size: 1.1rem; font-weight: 600; color: #333; margin: 1rem 0 .5rem; }
    .feed-item {
        background: white;
        border-left: 3px solid #ff6b35;
        padding: .6rem 1rem;
        border-radius: 0 10px 10px 0;
        margin-bottom: .5rem;
        font-size: .9rem;
    }
    .feed-date { font-size: .75rem; color: #999; }
    .weather-block {
        background: white;
        border-radius: 12px;
        padding: .8rem 1rem;
        text-align: center;
        font-size: .85rem;
    }
    .weather-temp { font-size: 1.4rem; font-weight: 700; }
    .fun-card {
        background: white;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin-bottom: .6rem;
        display: flex;
        align-items: center;
        gap: .8rem;
        box-shadow: 0 1px 4px rgba(0,0,0,.05);
    }
    .fun-icon { font-size: 1.6rem; }
    .fun-text { font-size: .9rem; color: #444; }
    .fun-highlight { font-weight: 700; color: #ff6b35; }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown("# 🚴 Roos's Fietsavontuur")
    start_date = datetime(2026, 3, 1)   # ← pas aan naar werkelijke startdatum
    days_on_road = (datetime.now() - start_date).days
    st.markdown(
        f"**Dag {max(days_on_road, 0)}** van de grote tocht &nbsp;·&nbsp; "
        f"<span class='update-pill'>live via Strava</span>",
        unsafe_allow_html=True,
    )
with col_h2:
    if st.button("🔄 Vernieuwen", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

st.divider()

# ── Data laden (gecacht 15 min) ──────────────────────────────────────────────
@st.cache_data(ttl=900, show_spinner="Strava data ophalen…")
def load_data():
    activities = get_all_activities(start_date="2026-01-01")  # ← aanpassen naar haar vertrekdatum
    return activities

with st.spinner("Data ophalen…"):
    activities = load_data()

totals = compute_totals(activities)
latest_pos = get_latest_position(activities)

# ── LAYOUT: kaart + stats ─────────────────────────────────────────────────────
map_col, stats_col = st.columns([3, 2], gap="medium")

# ── Kaart ─────────────────────────────────────────────────────────────────────
with map_col:
    st.markdown("<div class='section-title'>📍 Huidige locatie & route</div>", unsafe_allow_html=True)
    map_html = render_map(activities, latest_pos)
    st.components.v1.html(map_html, height=420, scrolling=False)

# ── Statistieken ─────────────────────────────────────────────────────────────
with stats_col:
    st.markdown("<div class='section-title'>📊 Totalen</div>", unsafe_allow_html=True)

    def metric_card(icon, value, label):
        return f"""
        <div class='metric-card'>
            <div class='metric-val'>{icon} {value}</div>
            <div class='metric-label'>{label}</div>
        </div>"""

    st.markdown(metric_card("🛣️", f"{totals['distance_km']:,.0f} km", "Totale afstand"), unsafe_allow_html=True)
    st.markdown(metric_card("⛰️", f"{totals['elevation_m']:,.0f} m", "Hoogtemeters geklommen"), unsafe_allow_html=True)
    st.markdown(metric_card("🏁", f"{totals['rides']}", "Ritten voltooid"), unsafe_allow_html=True)
    st.markdown(metric_card("🌍", f"{totals['countries']}", "Landen aangedaan"), unsafe_allow_html=True)
    st.markdown(metric_card("⏱️", f"{totals['moving_hours']:.0f} uur", "Rijdend onderweg"), unsafe_allow_html=True)

st.divider()

# ── Weer + Fun stats ──────────────────────────────────────────────────────────
weer_col, fun_col = st.columns([2, 3], gap="medium")

with weer_col:
    st.markdown("<div class='section-title'>🌤️ Weer onderweg</div>", unsafe_allow_html=True)
    if latest_pos:
        weather = get_weather(latest_pos["lat"], latest_pos["lon"])
        if weather:
            # Vandaag
            today = weather["today"]
            st.markdown(f"""
            <div class='weather-block' style='margin-bottom:.5rem'>
                <div style='font-size:.75rem;color:#999;margin-bottom:.3rem'>Vandaag · {latest_pos.get('city','onderweg')}</div>
                <div class='weather-temp'>{today['icon']} {today['temp_max']:.0f}°C</div>
                <div style='color:#666;font-size:.8rem'>{today['description']}</div>
                <div style='font-size:.78rem;color:#aaa;margin-top:.3rem'>
                    💧 {today['precip']:.1f}mm &nbsp; 💨 {today['wind']:.0f} km/h
                </div>
            </div>""", unsafe_allow_html=True)

            # 7-daagse voorspelling
            st.markdown("<div style='font-size:.8rem;color:#888;margin:.5rem 0 .3rem'>Komende 7 dagen</div>", unsafe_allow_html=True)
            cols_w = st.columns(7)
            for i, (day, col) in enumerate(zip(weather["forecast"], cols_w)):
                with col:
                    st.markdown(f"""
                    <div style='text-align:center;font-size:.72rem'>
                        <div style='color:#aaa'>{day['day']}</div>
                        <div style='font-size:1.1rem'>{day['icon']}</div>
                        <div style='font-weight:600'>{day['temp_max']:.0f}°</div>
                        <div style='color:#bbb'>{day['temp_min']:.0f}°</div>
                    </div>""", unsafe_allow_html=True)
    else:
        st.info("Locatie nog niet beschikbaar. Haal eerst een activiteit op via Strava.")

with fun_col:
    st.markdown("<div class='section-title'>🎉 Fun facts</div>", unsafe_allow_html=True)
    fun = compute_fun_stats(totals)
    for stat in fun:
        st.markdown(f"""
        <div class='fun-card'>
            <span class='fun-icon'>{stat['icon']}</span>
            <span class='fun-text'>{stat['text']}</span>
        </div>""", unsafe_allow_html=True)

st.divider()

# ── Activiteiten feed ─────────────────────────────────────────────────────────
st.markdown("<div class='section-title'>📝 Recente ritten</div>", unsafe_allow_html=True)
feed = build_feed(activities, n=8)
for item in feed:
    st.markdown(f"""
    <div class='feed-item'>
        <div class='feed-date'>{item['date']}</div>
        <strong>{item['name']}</strong> — {item['distance']:.1f} km
        &nbsp;·&nbsp; ⛰️ {item['elevation']:.0f}m
        &nbsp;·&nbsp; ⏱️ {item['duration']}
        {f" &nbsp;·&nbsp; 🔥 {item['kudos']} kudos" if item['kudos'] else ""}
    </div>""", unsafe_allow_html=True)

# ── Auto-refresh elke 15 min ──────────────────────────────────────────────────
st.markdown("""
<script>
setTimeout(function() { window.location.reload(); }, 900000);
</script>
""", unsafe_allow_html=True)

st.markdown(
    "<div style='text-align:center;font-size:.75rem;color:#ccc;margin-top:2rem'>"
    "gemaakt met ❤️ · updates via Strava · weer via Open-Meteo</div>",
    unsafe_allow_html=True,
)
