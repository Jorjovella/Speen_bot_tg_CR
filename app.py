from flask import Flask, request
import sqlite3
import datetime

app = Flask(__name__)
conn = sqlite3.connect("database.db", check_same_thread=False)
cur = conn.cursor()

# Создание таблицы при запуске
cur.execute("CREATE TABLE IF NOT EXISTS history (user_id TEXT, prize TEXT, time TEXT)")
conn.commit()

@app.route("/api/can_spin", methods=["POST"])
def can_spin():
    data = request.json
    user_id = data.get("code")  # пока получаем как "code" с фронта

    if not user_id:
        return {"can_spin": False, "error": "Missing user_id"}, 400

    cur.execute("SELECT 1 FROM history WHERE user_id = ?", (user_id,))
    already_spun = cur.fetchone() is not None
    return {"can_spin": not already_spun}

@app.route("/api/save_win", methods=["POST"])
def save_win():
    data = request.json
    user_id = data.get("code")  # тоже "code" с фронта, но это user_id
    prize = data.get("prize")

    if user_id and prize:
        # Защита от повторного сохранения
        cur.execute("SELECT 1 FROM history WHERE user_id = ?", (user_id,))
        if cur.fetchone():
            return {"status": "already_saved"}

        cur.execute(
            "INSERT INTO history (user_id, prize, time) VALUES (?, ?, ?)",
            (user_id, prize, datetime.datetime.now().isoformat())
        )
        conn.commit()
        print(f"[SAVE] user_id={user_id}, prize={prize}")  # лог
        return {"status": "ok"}

    return {"status": "error", "message": "Missing user_id or prize"}, 400

@app.route("/")
def home():
    return "✅ Backend работает!"
