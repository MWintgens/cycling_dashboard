# 🚴 Roos's Fietsavontuur — Travel Dashboard

Een live Streamlit-dashboard voor Roos's 6-maanden fietsreis.  
Toont Strava-stats, interactieve kaart, weersvoorspelling, fun facts en een activiteiten-feed.

---

## 📁 Projectstructuur

```
cycling_dashboard/
├── app.py                     # Hoofdapp (Streamlit)
├── requirements.txt
├── .streamlit/
│   └── secrets.toml.example  # Vul in en hernoem naar secrets.toml
└── utils/
    ├── strava.py              # Strava API-koppeling
    ├── weather.py             # Open-Meteo weer
    ├── stats.py               # Statistieken + fun facts
    ├── map.py                 # Folium-kaart
    └── feed.py                # Activiteiten-feed
```

---

## 🔑 Stap 1 — Strava API instellen

### 1a. Maak een Strava App
1. Ga naar https://www.strava.com/settings/api
2. Maak een nieuwe applicatie aan (naam maakt niet uit, zet `localhost` als callback-domein)
3. Noteer **Client ID** en **Client Secret**

### 1b. Haal een Refresh Token op (eenmalig)

Open deze URL in je browser (vervang `CLIENT_ID`):

```
https://www.strava.com/oauth/authorize?client_id=CLIENT_ID&response_type=code&redirect_uri=http://localhost&approval_prompt=force&scope=activity:read_all
```

Na het goedkeuren kopieer je de `code` uit de redirect-URL en doe je:

```bash
curl -X POST https://www.strava.com/oauth/token \
  -d client_id=CLIENT_ID \
  -d client_secret=CLIENT_SECRET \
  -d code=JOUW_CODE \
  -d grant_type=authorization_code
```

Kopieer de `refresh_token` uit de response. **Dit token hoef je nooit te vernieuwen** — de app doet dat automatisch.

### 1c. Sla op in secrets

Maak `.streamlit/secrets.toml` op basis van het `.example`-bestand:

```toml
STRAVA_CLIENT_ID     = "12345"
STRAVA_CLIENT_SECRET = "abc..."
STRAVA_REFRESH_TOKEN = "def..."
```

---

## 🖥️ Lokaal draaien

```bash
pip install -r requirements.txt
streamlit run app.py
```

De app draait op http://localhost:8501 — ook mooi te zien op iPhone via je lokale IP.

**Zonder Strava-koppeling** werkt de app gewoon met demo-data.

---

## ☁️ Hosten op Streamlit Cloud (gratis)

1. Push dit project naar een **private** GitHub-repo
2. Ga naar https://share.streamlit.io en koppel je repo
3. Ga naar **Settings → Secrets** en plak de inhoud van `secrets.toml`
4. Deploy — je krijgt een publieke URL die Roos kan bookmarken

---

## ✨ Features

| Feature | Hoe |
|---|---|
| 🗺️ Live kaart met route | Strava GPS-polylines via Folium |
| 📊 km + hoogtemeters | Strava API (alle ritten gecombineerd) |
| 🌍 Landen teller | Via Strava locatie-velden |
| 🌤️ Weer + 7-daags | Open-Meteo (gratis, geen key) |
| 🎉 Fun stats | Eiffeltorens, aardbol%, wielomwentelingen |
| 📝 Activiteiten-feed | Laatste 8 ritten met details |
| 🔄 Auto-refresh | Elke 15 minuten automatisch |
| 📱 iPhone-vriendelijk | Responsive Streamlit-layout |

---

## 🎨 Aanpassen

- **Startdatum**: pas `start_date` aan in `app.py` (regel ~38)
- **Naam**: zoek op "Roos" in `app.py` en vervang
- **Fun stats**: voeg vergelijkingen toe in `utils/stats.py`
- **Kleur**: het oranje `#ff6b35` is de hoofdkleur — zoek/vervang om te wijzigen
- **Landen**: verfijn de detectie in `utils/stats.py` met de Nominatim geocoder

---

## 📞 Hulp nodig?

De app draait ook zonder Strava (demo-modus) — handig om het cadeau al te laten zien
voordat de Strava-koppeling klaar is!
