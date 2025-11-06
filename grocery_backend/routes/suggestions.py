from flask import Flask, jsonify, Blueprint
import sqlite3
from ..config import DB_PATH

suggestions_bp = (Blueprint('suggestions', __name__))

@suggestions_bp.route('/', methods=['GET'])
def get_suggestions():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT name FROM items WHERE current = 0 AND total_purchases > 0 ORDER BY total_purchases DESC")
    suggested_list = [row[0] for row in c.fetchall()]

    conn.close()

    return jsonify(suggested_list)