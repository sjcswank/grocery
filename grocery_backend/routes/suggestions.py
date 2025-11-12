from flask import Flask, jsonify, Blueprint, request
import sqlite3
from ..config import DB_PATH, STORE_ID
import statistics
import json
from ..services import kroger_api

suggestions_bp = (Blueprint('suggestions', __name__))

@suggestions_bp.route('/', methods=['GET'])
def get_suggestions():
    userId = request.headers.get("userId")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()


    c.execute("""
        SELECT id, name, price, previous_purchased_prices
        FROM items 
        WHERE owner_id = ? AND current = 0 AND total_purchases > 0 
        ORDER BY total_purchases DESC
        """, (userId,))
    suggested_list = [
        {'id': row[0], 'name': row[1], 'price': row[2], 'previous_purchase_prices': row[3], 'sale': False} for row in c.fetchall()
    ]
    conn.close()

    # Is current price lower than average?
    for item in suggested_list:
        token = kroger_api.getToken()
        product_data = kroger_api.getProduct(item['name'], STORE_ID, token)

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
        item['price'] = sorted_by_price[0]['price']

        difference = 0
        previous_purchased_prices_string = item['previous_purchase_prices']

        try:
            previous_purchased_prices_list = json.loads(previous_purchased_prices_string)
            previous_purchased_prices = [float(s) for s in previous_purchased_prices_list]
        except Exception as e:
            previous_purchased_prices = []
            print(e)

        if len(previous_purchased_prices) > 0:
            average_price = statistics.mean(previous_purchased_prices)
            difference = average_price - float(item['price']) 
        else:
            print(previous_purchased_prices)

        if difference >= .25:
                item['sale'] = True


    return jsonify(suggested_list)