from flask import Flask, jsonify, render_template
import sqlite3

app = Flask(__name__)

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

temp = 60
alarm = check_anomaly(temp)

save_data(temp, "Kochen", alarm)


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

app.run(host="0.0.0.0", port=5000, debug=True)
