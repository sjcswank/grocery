from flask import Flask, jsonify, Blueprint, request
import sqlite3
from ..config import DB_PATH

previous_bp = (Blueprint('previous', __name__))

@previous_bp.route('/', methods=['GET'])
def get_previous_items(top_n=10):
    userId = request.headers.get("userId")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        SELECT name, last_purchase_date
        FROM items
        WHERE owner_id = ? AND total_purchases > 0
        ORDER BY last_purchase_date DESC
        LIMIT ?
    """,
        (userId, top_n),
    )
    items = [row[0] for row in c.fetchall()]
    conn.close()

    return jsonify(items)