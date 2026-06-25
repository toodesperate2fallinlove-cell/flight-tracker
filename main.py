from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

IGNAV_API_KEY = os.getenv("IGNAV_API_KEY")


@app.route("/")
def home():
    return "Flight Tracker API is running!"


@app.route("@app.route("/search")
def search():
    origin = request.args.get("origin")
    destination = request.args.get("destination")
    date = request.args.get("date")

    url = "https://ignav.com/api/fares/one-way"

    headers = {
        "X-Api-Key": IGNAV_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "origin": origin,
        "destination": destination,
        "departure_date": date
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload
    )

    data = response.json()

    html = f"<h1>Flights from {origin} to {destination}</h1>"

    for flight in data.get("itineraries", []):
        carrier = flight["outbound"]["carrier"]
        price = flight["price"]["amount"]
        currency = flight["price"]["currency"]
        duration = flight["outbound"]["duration_minutes"]

        html += f"""
        <div style='border:1px solid black;
                    margin:10px;
                    padding:10px'>
            <h3>{carrier}</h3>
            <p>Price: {price} {currency}</p>
            <p>Duration: {duration} minutes</p>
        </div>
        """

    return html")
def search():
    origin = request.args.get("origin")
    destination = request.args.get("destination")
    date = request.args.get("date")

    if not origin or not destination or not date:
        return jsonify({
            "error": "Please provide origin, destination and date"
        }), 400

    url = "https://ignav.com/api/fares/one-way"

    headers = {
        "X-Api-Key": IGNAV_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "origin": origin,
        "destination": destination,
        "departure_date": date
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=30
    )

    return jsonify(response.json())


@app.route("/test")
def test():
    url = "https://ignav.com/api/fares/one-way"

    headers = {
        "X-Api-Key": IGNAV_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "origin": "DEL",
        "destination": "CMB",
        "departure_date": "2026-07-20"
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=30
    )

    return jsonify(response.json())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
