from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

IGNAV_API_KEY = os.getenv("IGNAV_API_KEY")


@app.route("/")
def home():
    return """
    <h1>Delhi Flight Tracker ✈️</h1>

    <form action="/search">
        <p>Origin Airport</p>
        <input name="origin" placeholder="DEL" required>

        <p>Destination Airport</p>
        <input name="destination" placeholder="KUL" required>

        <p>Date</p>
        <input name="date" type="date" required>

        <br><br>
        <button type="submit">Search Flights</button>
    </form>

    <br>

    <p>
    Example cheapest search:
    <a href="/cheapest?date=2026-07-20">
    Cheapest Flights From Delhi
    </a>
    </p>
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
            price_text = f"₹{inr_price:,}"
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
        return """
        <h2>Please provide a date.</h2>
        Example:
        /cheapest?date=2026-07-20
        """

    destinations = {
     "Colombo": "CMB",
    "Bali": "DPS",
    "Kuala Lumpur": "KUL",
    "Bangkok": "BKK",
    "Singapore": "SIN",
    "Mauritius": "MRU",
    "Male": "MLE",
    "Phuket": "HKT"
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
            <p>Approx Price: ₹{inr_price:,}</p>
        </div>
        """

    return html


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
