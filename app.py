from flask import Flask, Response
import requests
from datetime import datetime, timezone

app = Flask(__name__)

ZONE_TARGET = "NYC007"
NWS_URL = f"https://api.weather.gov/alerts/active?zone={ZONE_TARGET}"

def fetch_tioga_alerts():
    try:
        response = requests.get(NWS_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        return f"; Error fetching alerts: {e}\n"

    lines = [
        "Title: Tioga County NY - Live NWS Warnings (Zone NYC007)",
        "RefreshSeconds: 60"
    ]

    for feature in data.get("features", []):
        props = feature.get("properties", {})
        geometry = feature.get("geometry")
        event = props.get("event", "Unknown Event")
        severity = props.get("severity", "Unknown")
        coords = []

        if not geometry:
            continue

        if geometry.get("type") == "Polygon":
            coords = geometry.get("coordinates", [[]])[0]
        elif geometry.get("type") == "MultiPolygon":
            coords = geometry.get("coordinates", [[[]]])[0][0]
        else:
            continue

        if not coords:
            continue

        # Color-coding with lime green for Flood warnings
        if "Tornado" in event:
            color = "255 0 0"           # Red
        elif "Severe" in event:
            color = "255 165 0"         # Orange
        elif "Flood" in event:
            color = "50 205 50"         # Lime green
        else:
            color = "255 255 0"         # Yellow

        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        lines.append(f"Color: {color}")
        lines.append(f"; {event} | Severity: {severity} | Updated: {timestamp}")
        lines.append("Polygon:")
        for lon, lat in coords:
            lines.append(f"{lat}, {lon}")
        lines.append("End:")

    return "\n".join(lines) if len(lines) > 2 else "; No active warnings for Tioga County NY"

@app.route("/live.pf")
def serve_placefile():
    return Response(fetch_tioga_alerts(), mimetype="text/plain")

@app.route("/")
def home():
    return "<h2>Tioga County Placefile API</h2><p>Use <code>/live.pf</code> in GRLevel3.</p>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
