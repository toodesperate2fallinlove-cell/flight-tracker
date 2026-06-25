```python
from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

IGNAV_API_KEY = os.getenv("IGNAV_API_KEY")


@app.route("/")
def home():
    return """
    <h1>Delhi Flight Tracker ✈️</h1>

    <h2>One-Way Flight Search</h2>

    <form action="/search">
        <p>Origin Airport</p>
        <input name="origin" placeholder="DEL" required>

        <p>Destination Airport</p>
        <input name="destination" placeholder="DPS" required>

        <p>Departure Date</p>
        <input name="date" type="date" required>

        <br><br>
        <button type="submit">Search Flights</button>
    </form>

    <hr>

    <h2>Cheapest Destinations From Delhi</h2>

    <form action="/cheapest">
        <p>Date</p>
        <input name="date" type="date" required>

        <br><br>
        <button type="submit">
            Find Cheapest Destinations
        </button>
    </form>

    <hr>

    <h2>Round Trip Search</h2>

    <form action="/roundtrip">
        <p>Origin Airport</p>
        <input name="origin" placeholder="DEL" required>

        <p>Destination Airport</p>
        <input name="destination" placeholder="DPS" required>

        <p>Departure Date</p>
        <input name="departure_date" type="date" required>

        <p>Return Date</p>
        <input name="return_date" type="date" required>

        <br><br>
        <button type="submit">
            Search Round Trip
        </button>
    </form>
    """


@app.route("/search")
def search():
    origin = request.args.get("origin")
    destination = request.args.get("destination")
    date = request.args.get("date")

    if not origin or not destination or not date:
        return "Please provide origin, destination and date."

    url = "https://ignav.com/api/fares/one-way"

    headers = {
        "X-Api-Key": IGNAV_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "origin": origin.upper(),
        "destination": destination.upper(),
        "departure_date": date
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=30
    )

    data = response.json()
    itineraries = data.get("itineraries", [])

    html = f"<h1>Flights from {origin.upper()} to {destination.upper()}</h1>"

    if not itineraries:
        return html + "<p>No flights found.</p>"

    for flight in itineraries:
        carrier = flight["outbound"]["carrier"]
        price = flight["price"]["amount"]
        currency = flight["price"]["currency"]
        duration = flight["outbound"]["duration_minutes"]

        if currency == "USD":
            inr_price = int(price * 86)
            price_text = f"${price} (≈ ₹{inr_price:,})"
        else:
            price_text = f"{price} {currency}"

        html += f"""
        <div style='border:1px solid #ccc;
                    margin:10px;
                    padding:10px'>
            <h3>{carrier}</h3>
            <p>Price: {price_text}</p>
            <p>Duration: {duration} minutes</p>
        </div>
        """

    return html


@app.route("/airports")
def airports():
    q = request.args.get("q")

    if not q:
        return jsonify({
            "error": "Please provide q parameter"
        }), 400

    url = "https://ignav.com/api/airports"

    headers = {
        "X-Api-Key": IGNAV_API_KEY
    }

    params = {
        "q": q,
        "limit": 10
    }

    response = requests.get(
        url,
        headers=headers,
        params=params,
        timeout=15
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


@app.route("/cheapest")
def cheapest():
    date = request.args.get("date")

    if not date:
        return "Please provide a date."

    destinations = {
        "Colombo": "CMB",
        "Bali (Denpasar)": "DPS",
        "Jakarta": "CGK",
        "Surabaya": "SUB",
        "Bangkok": "BKK",
        "Phuket": "HKT",
        "Krabi": "KBV",
        "Chiang Mai": "CNX",
        "Kuala Lumpur": "KUL",
        "Penang": "PEN",
        "Langkawi": "LGK",
        "Singapore": "SIN",
        "Mauritius": "MRU",
        "Seychelles (Mahe)": "SEZ",
        "Male": "MLE",
        "Ho Chi Minh City": "SGN",
        "Hanoi": "HAN",
        "Da Nang": "DAD",
        "Phnom Penh": "PNH",
        "Siem Reap": "SAI",
        "Vientiane": "VTE",
        "Luang Prabang": "LPQ",
        "Port Blair (Andaman)": "IXZ"
    }

    results = []

    url = "https://ignav.com/api/fares/one-way"

    headers = {
        "X-Api-Key": IGNAV_API_KEY,
        "Content-Type": "application/json"
    }

    for city, code in destinations.items():
        payload = {
            "origin": "DEL",
            "destination": code,
            "departure_date": date
        }

        try:
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=15
            )

            data = response.json()
            itineraries = data.get("itineraries", [])

            if itineraries:
                cheapest_price = min(
                    i["price"]["amount"]
                    for i in itineraries
                )

                results.append(
                    (city, code, cheapest_price)
                )

        except Exception:
            pass

    results.sort(key=lambda x: x[2])

    html = f"<h1>Cheapest Flights From Delhi ({date}) ✈️</h1>"

    if not results:
        return html + "<p>No flights found.</p>"

    for city, code, price in results:
        inr_price = int(price * 86)

        html += f"""
        <div style='border:1px solid #ccc;
                    margin:10px;
                    padding:10px'>
            <h3>{city} ({code})</h3>
            <p>${price} (≈ ₹{inr_price:,})</p>
        </div>
        """

    return html


@app.route("/roundtrip")
def roundtrip():
    origin = request.args.get("origin")
    destination = request.args.get("destination")
    departure_date = request.args.get("departure_date")
    return_date = request.args.get("return_date")

    if not origin or not destination or not departure_date or not return_date:
        return "Please provide all fields."

    url = "https://ignav.com/api/fares/round-trip"

    headers = {
        "X-Api-Key": IGNAV_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "origin": origin.upper(),
        "destination": destination.upper(),
        "departure_date": departure_date,
        "return_date": return_date
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=30
    )

    data = response.json()
    itineraries = data.get("itineraries", [])

    html = f"""
    <h1>
    Round Trip:
    {origin.upper()} → {destination.upper()}
    </h1>

    <p>
    Departure: {departure_date}<br>
    Return: {return_date}
    </p>
    """

    if not itineraries:
        return html + "<p>No flights found.</p>"

    for flight in itineraries:
        price = flight["price"]["amount"]
        currency = flight["price"]["currency"]

        if currency == "USD":
            inr_price = int(price * 86)
            price_text = f"${price} (≈ ₹{inr_price:,})"
        else:
            price_text = f"{price} {currency}"

        html += f"""
        <div style='border:1px solid #ccc;
                    margin:10px;
                    padding:10px'>
            <h3>{price_text}</h3>
        </div>
        """

    return html


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
```
