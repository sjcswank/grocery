from flask import Flask, request, jsonify, Blueprint
import sqlite3
from datetime import datetime
from ..config import DB_PATH
from ..services import mealme_api
from ..services import kroger_api
import json


items_bp = Blueprint('items', __name__)


@items_bp.route("/", methods=["GET"])
def get_items():
    userId = request.headers.get("userId")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT id, name, bought, prices FROM items WHERE owner_id = ? AND current = 1", (userId,))
    items = [
        {"id": row[0], "name": row[1], "bought": bool(row[2]), "prices": row[3]} for row in c.fetchall()
    ]
    conn.close()

    return jsonify(items)


@items_bp.route("/", methods=["POST"])
def add_item():
    userId = request.headers.get("userId")
    data = request.json

    # DONE Make call to prices API
    token = kroger_api.getToken()

    # location_ids = kroger_api.getLocations('63127', token) # 61500122

    product_data = kroger_api.getProduct(data['name'], '61500122', token)

    info = {
        'price': product_data['data'][0]['items'][0]['price']['regular'],
        'fulfillment': product_data['data'][0]['items'][0]['fulfillment'], # {"curbside": true, "delivery": true, "inStore": true, "shipToHome": false},
        'inventory': product_data['data'][0]['items'][0]['inventory'], # {"stockLevel": "HIGH"},
        'itemId': product_data['data'][0]['items'][0]['itemId'],
        'size': product_data['data'][0]['items'][0]['size'],
        'brand': product_data['data'][0]['brand'],
        'category': product_data['data'][0]['categories'][0],
        'description': product_data['data'][0]['description'],
        'images': product_data['data'][0]['images']
    }
    prices = info['price']

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT id, current FROM items WHERE name = ? AND owner_id = ?", (data["name"], userId))
    item = c.fetchone()
    if item:
        c.execute(
            "UPDATE items SET current = 1, bought = 0, prices = ? WHERE id = ?",
            (prices, item[0]),
        )
        conn.commit()
        item_id = item[0]
        print("updated item")
    else:
        try:
            c.execute(
                "INSERT INTO items (name, current, created_at, owner_id, prices) VALUES (?, ?, ?, ?, ?)",
                (data["name"], 1, datetime.now(), userId, prices),
            )
            item_id = c.lastrowid
            conn.commit()
        except sqlite3.IntegrityError:
            print("Insert failed")
    conn.close()

    return jsonify({"id": item_id, "name": data["name"], "bought": False, "prices": prices}), 201


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
    data = request.json
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute('SELECT name, bought, total_purchases, previous_purchased_prices FROM items WHERE id = ?', (item_id,))
    result = c.fetchone()

    if result and result[1]:
        previous_purchased_prices_string = result[3]
        try:
            previous_purchased_prices = json.loads(previous_purchased_prices_string) 
        except:
            previous_purchased_prices = []
        previous_purchased_prices.append(data['price'])
        updated_previous_prices = json.dumps(previous_purchased_prices)

        c.execute("""
            UPDATE items
            SET current = 0, total_purchases = ?, last_purchase_date = ?, bought = 0, previous_purchased_prices = ?
            WHERE id =?
        """, (result[2] + 1, datetime.now(), updated_previous_prices, item_id))
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