from flask import Flask, request, jsonify, Blueprint
import sqlite3
from datetime import datetime
from ..config import DB_PATH


auth_bp = Blueprint('auth', __name__)


@auth_bp.route("/", methods=["POST"])
def add_user():
    data = request.json
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT id FROM users WHERE username = ? OR email = ?", (data["username"], data["email"]))
    item = c.fetchone()
    if item:
        return "User exists."
    else:
        c.execute("""
            INSERT INTO users 
            (username, email, password, created_at) 
            VALUES (?, ?, ?, ?)""", 
            (data['username'], data['email'], data['password'], datetime.now())
            )
        user_id = c.lastrowid
        conn.commit()
    conn.close()

    return jsonify({"id": user_id, "username": data['username'], "email": data['email']})

@auth_bp.route("/login", methods=["POST"])
def login_user():
    data = request.json
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT id, username, email FROM users WHERE username = ? AND password = ?", (data["username"], data["password"]))
    user = c.fetchone()
    conn.close()

    if user:
        return jsonify({"id": user[0], "username": user[1], "email": user[2]})
    else:
        return 'User does not exist.'