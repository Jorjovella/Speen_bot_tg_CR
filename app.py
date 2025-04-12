from flask import Flask, request
import sqlite3
import datetime

app = Flask(__name__)
conn = sqlite3.connect("database.db", check_same_thread=False)
cur = conn.cursor()

# Создаём таблицу при запуске
cur.execute("CREATE TABLE IF NOT EXISTS history (user_id TEXT, prize TEXT, time TEXT)")
conn.commit()

@app.route("/api/can_spin", methods=["POST"])
def can_spin():
    data = request.json
    code = data.get("code")
    if not code:
        return {"can_spin": False}, 400

    cur.execute("SELECT 1 FROM history WHERE user_id = ?", (code,))
    already_used = cur.fetchone() is not None
    return {"can_spin": not already_used}

@app.route("/api/save_win", methods=["POST"])
def save_win():
    data = request.json
    code = data.get("code")
    prize = data.get("prize")

    if code and prize:
        cur.execute("SELECT 1 FROM history WHERE user_id = ?", (code,))
        if cur.fetchone():
            return {"status": "already_saved"}

        cur.execute("INSERT INTO history (user_id, prize, time) VALUES (?, ?, ?)",
                    (code, prize, datetime.datetime.now().isoformat()))
        conn.commit()
        return {"status": "ok"}

    return {"status": "error"}, 400

@app.route("/")
def home():
    return "✅ Backend работает!"
