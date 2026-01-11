from flask import Flask, request, jsonify, Blueprint
import sqlite3
from datetime import datetime
from ..config import DB_PATH, STORE_ID
from ..services import kroger_api
import json


items_bp = Blueprint('items', __name__)


@items_bp.route("/", methods=["GET"])
def get_items():
    userId = request.headers.get("userId")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT id, name, bought, price FROM items WHERE owner_id = ? AND current = 1", (userId,))
    items = [
        {"id": row[0], "name": row[1], "bought": bool(row[2]), "price": row[3]} for row in c.fetchall()
    ]
    conn.close()

    return jsonify(items)


@items_bp.route("/", methods=["POST"])
def add_item():
    userId = request.headers.get("userId")
    data = request.json

    token = kroger_api.getToken()

    # location_ids = kroger_api.getLocations('63127', token) # 61500122

    product_data = kroger_api.getProduct(data['name'], STORE_ID, token)

    products = []
    for product in product_data['data']:
        info = {
            'description': product['description'],
            'price': product['items'][0]['price']['regular'],
            'images': product['images'],
            'itemId': product['items'][0]['itemId']
        }
        products.append(info)
    sorted_by_price = sorted(products, key=lambda x: x['price'])

    # info = {
    #     # 'fulfillment': product_data['data'][0]['items'][0]['fulfillment'], # {"curbside": true, "delivery": true, "inStore": true, "shipToHome": false},
    #     # 'inventory': product_data['data'][0]['items'][0]['inventory'], # {"stockLevel": "HIGH"},
    #     # 'itemId': product_data['data'][0]['items'][0]['itemId'],
    #     # 'size': product_data['data'][0]['items'][0]['size'],
    #     # 'brand': product_data['data'][0]['brand'],
    #     # 'category': product_data['data'][0]['categories'][0],
    # }

    #TODO: Refactor to return list of product options for selection
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT id, current FROM items WHERE name = ? AND owner_id = ?", (sorted_by_price[0]['description'], userId))
    item = c.fetchone()
    if item:
        c.execute(
            "UPDATE items SET current = 1, bought = 0, price = ?, name = ? WHERE id = ?",
            (sorted_by_price[0]['price'], sorted_by_price[0]['description'], item[0]),
        )
        conn.commit()
        item_id = item[0]
    else:
        try:
            c.execute(
                "INSERT INTO items (name, current, created_at, owner_id, price) VALUES (?, ?, ?, ?, ?)",
                (sorted_by_price[0]['description'], 1, datetime.now(), userId, sorted_by_price[0]['price']),
            )
            item_id = c.lastrowid
            conn.commit()
        except sqlite3.IntegrityError:
            print("Insert failed")
    conn.close()

    return jsonify({"id": item_id, "name": sorted_by_price[0]['description'], "bought": False, "price": sorted_by_price[0]['price']}), 201


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