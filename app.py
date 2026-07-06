from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import os

app = Flask(__name__)
CORS(app)

CSV_FILE = "data.csv"


@app.route("/api/status", methods=["GET"])
def api_status():

    if not os.path.exists(CSV_FILE):
        return jsonify({"error": "CSV file not found"}), 404

    df = pd.read_csv(CSV_FILE)

    if df.empty:
        return jsonify({"error": "CSV is empty"}), 404

    last = df.iloc[-1]

    response = {
        # ===== Données CSV =====
        "timestamp": last["timestamp"],
        "k1_temperatur": float(last["k1_temperatur"]),
        "k2_temperatur": float(last["k2_temperatur"]),
        "k3_temperatur": float(last["k3_temperatur"]),
        "k2_fuellstand": float(last["k2_fuellstand"]),
        "k3_fuellstand": float(last["k3_fuellstand"]),
        "durchfluss": float(last["durchfluss"]),
        "aktueller_schritt": int(last["aktueller_schritt"]),
        "alarm": bool(last["alarm"]),

        # ===== Champs compatibles Dashboard =====
        "k1Temperature": float(last["k1_temperatur"]),
        "k2Temperature": float(last["k2_temperatur"]),
        "k3Temperature": float(last["k3_temperatur"]),

        "k2Level": float(last["k2_fuellstand"]),
        "k3Level": float(last["k3_fuellstand"]),

        "flowRate": float(last["durchfluss"]),

        "currentStep": int(last["aktueller_schritt"]),

        "phase": "Maischen",

        "alarmStatus": bool(last["alarm"]),

        "backend": "online"
    }

    return jsonify(response)


@app.route("/api/history", methods=["GET"])
def api_history():

    if not os.path.exists(CSV_FILE):
        return jsonify([])

    df = pd.read_csv(CSV_FILE)

    return jsonify(df.to_dict(orient="records"))


@app.route("/api/control", methods=["POST"])
def api_control():

    data = request.json

    return jsonify({
        "success": True,
        "message": "Control command received",
        "received": data
    })


@app.route("/", methods=["GET"])
def home():

    return jsonify({
        "message": "Brauanlage Flask API läuft",
        "status": "online",
        "endpoints": {
            "status": "/api/status",
            "history": "/api/history",
            "control": "/api/control"
        }
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

