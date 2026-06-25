@app.route("/test")
def test():
    import requests
    import os

    url = "https://ignav.com/api/fares/one-way"

    headers = {
        "X-Api-Key": os.getenv("IGNAV_API_KEY"),
        "Content-Type": "application/json"
    }

    payload = {
        "origin": "DEL",
        "destination": "CMB",
        "departure_date": "2026-07-25"
    }

    response = requests.post(url, headers=headers, json=payload)
    return response.json()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
