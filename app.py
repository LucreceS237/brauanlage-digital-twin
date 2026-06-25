from flask import Flask, jsonify, render_template
import sqlite3
import asyncio
from asyncua import Client
import logging
import paho.mqtt.publish as publish

temp = 67

publish.single(
    "brewery/temperature/mash",
    str(temp),
    hostname="localhost"
)

def publish_temperature(temp):

    publish.single(
        "brewery/temperature/mash",
        str(temp),
        hostname="localhost"
    )

    print("MQTT Temperatur gesendet:", temp)

logging.basicConfig(level=logging.INFO)
logging.info("Server started")

app = Flask(__name__)

# =========================
# OPC-UA
# =========================

url = "opc.tcp://192.168.0.1:4840"


async def read_opcua_data():

    async with Client(url=url) as client:

        print("Verbindung erfolgreich")

        temp_node = client.get_node(
            'ns=3;s="AL1401_X1_Temperatursensor_Gärung"."Temperatur"'
        )

        temp = await temp_node.read_value()

        return temp

# =========================
# DATABASE
# =========================


def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        temperature REAL,
        phase TEXT, 
        alarm INTEGER
    )
    """)

    conn.commit()
    conn.close()


def save_data(temp, phase, alarm):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO data (temperature, phase, alarm) VALUES (?, ?, ?)",
        (temp, phase, alarm)
    )

    conn.commit()
    conn.close()


# =========================
# ANOMALY
# =========================

def check_anomaly(temp):

    if temp > 75:
        return True

    return False


# =========================
# INIT
# =========================

init_db()

# test data

try:

    temp = asyncio.run(read_opcua_data())

    phase = "Kochen"

    alarm = check_anomaly(temp)

    save_data(temp, phase, alarm)

except Exception as e:

    print("OPC-UA Error:", e)


# =========================
# API STATUS
# =========================

@app.route("/api/status")
def status():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM data ORDER BY id DESC LIMIT 1")

    row = cursor.fetchone()

    conn.close()

    if row:
        return jsonify({
            "temperature": row[1],

            "phase": row[2],

            "pump": True,

            "valve": False,

            "alarm": bool(row[3])
        })

    return jsonify({"message": "no data"})


# =========================
# DASHBOARD
# =========================

@app.route("/")
def dashboard():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM data ORDER BY id DESC LIMIT 1")

    row = cursor.fetchone()

    conn.close()

    if row:
        data = {
            "temperature": row[1],
            "phase": row[2],
            "alarm": bool(row[3])
        }

        return render_template("dashboard.html", data=data)

    return "No data"

@app.route("/history")
def history_page():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM data")

    rows = cursor.fetchall()

    conn.close()

    return render_template("history.html", rows=rows)

@app.route("/api/alarm")
def alarm():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM data ORDER BY id DESC LIMIT 1")

    row = cursor.fetchone()

    conn.close()

    if row:

        return jsonify({
            "alarm": bool(row[3])
        })

    return jsonify({"alarm": False})

app.run(host="0.0.0.0", port=5000, debug=True)
