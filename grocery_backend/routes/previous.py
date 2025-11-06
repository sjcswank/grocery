from flask import Flask, jsonify, Blueprint
import sqlite3
from ..config import DB_PATH

previous_bp = (Blueprint('previous', __name__))

@previous_bp.route('/', methods=['GET'])
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