from flask import Flask, Response
import requests
from datetime import datetime, timezone

app = Flask(__name__)

ZONE_TARGET = "NYZ059"
NWS_URL = f"https://api.weather.gov/alerts/active?zone={ZONE_TARGET}"

def fetch_tioga_alerts():
    try:
        response = requests.get(NWS_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        return f"; Error fetching alerts: {e}\n"

    lines = [
        "Title: Tioga County NY - Live NWS Warnings (By Zone)",
        "Refresh: 60"
    ]

    for feature in data.get("features", []):
        props = feature.get("properties", {})
        geometry = feature.get("geometry", {})
        event = props.get("event", "Unknown Event")
        severity = props.get("severity", "Unknown")
        updated = props.get("sent", "")
        coords = geometry.get("coordinates", [[]])[0]

        if not coords:
            continue

        # Color coding
        if "Tornado" in event:
            color = "255 0 0"
        elif "Severe" in event:
            color = "255 165 0"
        elif "Flash Flood" in event:
            color = "0 0 255"
        else:
            color = "255 255 0"

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
    content = fetch_tioga_alerts()
    return Response(content, mimetype="text/plain")

@app.route("/")
def home():
    return "<h2>Tioga County Placefile API</h2><p>Use <code>/live.pf</code> to load in GRLevel3.</p>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
