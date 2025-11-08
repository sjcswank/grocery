from flask import Flask, request, jsonify, Blueprint
import sqlite3
from datetime import datetime
from ..config import DB_PATH


items_bp = Blueprint('items', __name__)


@items_bp.route("/", methods=["GET"])
def get_items():
    userId = request.headers.get("userId")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT id, name, bought FROM items WHERE owner_id = ? AND current = 1", (userId,))
    items = [
        {"id": row[0], "name": row[1], "bought": bool(row[2])} for row in c.fetchall()
    ]
    conn.close()

    return jsonify(items)


@items_bp.route("/", methods=["POST"])
def add_item():
    userId = request.headers.get("userId")
    data = request.json
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT id, current FROM items WHERE name = ? AND owner_id = ?", (data["name"], userId))
    item = c.fetchone()
    if item:
        c.execute(
            "UPDATE items SET current = 1, bought = 0 WHERE id = ?",
            (item[0],),
        )
        conn.commit()
        item_id = item[0]
        print("updated item")
    else:
        try:
            c.execute(
                "INSERT INTO items (name, current, created_at, owner_id) VALUES (?, ?, ?, ?)",
                (data["name"], 1, datetime.now(), userId),
            )
            item_id = c.lastrowid
            conn.commit()
        except sqlite3.IntegrityError:
            print("Insert failed")
    conn.close()

    return jsonify({"id": item_id, "name": data["name"], "bought": False}), 201


@items_bp.route("/<int:item_id>", methods=["PATCH"])
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



@items_bp.route("/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute('SELECT name, bought, total_purchases FROM items WHERE id = ?', (item_id,))
    result = c.fetchone()

    if result and result[1]:
        c.execute("""
            UPDATE items
            SET current = 0, total_purchases = ?, last_purchase_date = ?, bought = 0
            WHERE id =?
        """, (result[2] + 1, datetime.now(), item_id))
    elif result and result[2] > 0:
        c.execute("""
            UPDATE items
            SET current = 0, bought = 0
            WHERE id =?
        """, (item_id,))
    else:
        c.execute('DELETE FROM items WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()

    return jsonify({'success': True})