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
        current INTEGER DEFAULT 0,
        bought INTEGER DEFAULT 0,
        total_purchases INTEGER DEFAULT 0,
        last_purchase_date TIMESTAMP,
        created_at TIMESTAMP
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

    c.execute("SELECT id, name, bought FROM items WHERE current = 1")
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

    c.execute("SELECT id, current FROM items WHERE name = ?", (data["name"],))
    item = c.fetchone()
    if item:
        c.execute(
            "UPDATE items SET current = 1, bought = 0 WHERE id = ?",
            (item[0],),
        )
        conn.commit()
        item_id = item[0]
        print("updated item")

    try:
        c.execute(
            "INSERT INTO items (name, current, created_at) VALUES (?, ?, ?)",
            (data["name"], 1, datetime.now()),
        )
        item_id = c.lastrowid
        conn.commit()
    except sqlite3.IntegrityError:
        print("Insert failed")
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

    c.execute('SELECT name, bought, total_purchases FROM items WHERE id = ?', (item_id,))
    result = c.fetchone()

    if result and result[1]:
        c.execute("""
            UPDATE items
            SET current = 0, total_purchases = ?, last_purchase_date = ?
            WHERE id =?
        """, (result[2] + 1, datetime.now(), item_id))
    elif result:
        c.execute("""
            UPDATE items
            SET current = 0
            WHERE id =?
        """, (item_id,))
    else:
        c.execute('DELETE FROM items WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()

    return jsonify({'success': True})


@app.route('/api/previous', methods=['GET'])
def get_previous_items(top_n=10):

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        SELECT name, last_purchase_date
        FROM items
        WHERE total_purchases > 0
        ORDER BY last_purchase_date DESC
        LIMIT ?
    """,
        (top_n,),
    )
    items = [row[0] for row in c.fetchall()]
    conn.close()

    return jsonify(items)


@app.route('/api/suggested', methods=['GET'])
def get_suggested():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT name FROM items WHERE current = 0 AND total_purchases > 0 ORDER BY total_purchases DESC")
    suggested_list = [row[0] for row in c.fetchall()]

    conn.close()

    return jsonify(suggested_list)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
