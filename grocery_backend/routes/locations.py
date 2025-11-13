from flask import Flask, request, jsonify, Blueprint
import sqlite3
from datetime import datetime
from ..config import DB_PATH, STORE_ID
from ..services import kroger_api
import json

locations_bp = Blueprint('locations', __name__)

@locations_bp.route("/", methods=["GET"])
def getNearbyLocations():
    token = kroger_api.getToken()
    locations_data = kroger_api.getLocations(63127, token)

    locations = []
    for location in locations_data['data']:
        info = {
            'address': location['address'],
            'locationId': location['locationId'],
            'name': location['name'],
            'phone': location['phone']
        }
        locations.append(info)
    return jsonify(locations)