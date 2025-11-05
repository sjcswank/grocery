from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime

app = Flask(__name__)
CORS(app)

DB_PATH = "grocery-backend/grocery.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        bought INTEGER DEFAULT 0,
        created_at TIMESTAMP
        )
    """
    )
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS previous_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_name TEXT NOT NULL,
        bought_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )
    conn.commit()
    conn.close()


# Create DB
init_db()


@app.route("/api/items", methods=["GET"])
def get_items():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT id, name, bought FROM items")
    items = [
        {"id": row[0], "name": row[1], "bought": bool(row[2])} for row in c.fetchall()
    ]
    conn.close()

    return jsonify(items)


@app.route("/api/items", methods=["POST"])
def add_item():
    data = request.json
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    try:
        c.execute(
            "INSERT INTO items (name, created_at) VALUES (?, ?)",
            (data["name"], datetime.now()),
        )
        conn.commit()
        print(f"Item '{data["name"]}' added successfully.")
        item_id = c.lastrowid
    except sqlite3.IntegrityError:
        print(f"Item '{data["name"]}' already exists.")
    conn.close()

    return jsonify({"id": item_id, "name": data["name"], "bought": False}), 201


@app.route("/api/items/<int:item_id>", methods=["PATCH"])
def toggle_bought(item_id):
    data = request.json
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        UPDATE items
        SET bought = ?
        WHERE id = ?
    """, 
        (1 if data['bought'] else 0, item_id),
    )
    conn.commit()
    conn.close()

    return jsonify({'success': True})


@app.route("/api/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    # data = request.json
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute('SELECT name, bought FROM items WHERE id = ?', (item_id,))
    result = c.fetchone()

    if result and result[1]:
        c.execute("""
            INSERT OR REPLACE INTO previous_items (item_name, bought_date)
            VALUES (?, ?)
        """,
            (result[0], datetime.now()),
        )
    c.execute('DELETE FROM items WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()

    return jsonify({'success': True})


@app.route('/api/previous')
def get_previous_items(top_n=10):

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        SELECT item_name, bought_date
        FROM previous_items
        ORDER BY bought_date DESC
        LIMIT ?
    """,
        (top_n,),
    )
    items = [row[0] for row in c.fetchall()]
    conn.close()

    return jsonify(items)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
