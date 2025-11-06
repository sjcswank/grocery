from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime
from . import create_app
from .config import DB_PATH, DEBUG, PORT
from .models import items


# DB_PATH = "grocery_backend/grocery.db"

def init_db():
    items.create_table()


# Create DB
init_db()

# Create App
app = create_app()


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
    app.run(debug=DEBUG, port=PORT)
