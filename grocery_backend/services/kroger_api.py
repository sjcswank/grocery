from flask import Flask, request, jsonify
import requests
from requests.auth import HTTPBasicAuth
from ..config import KROGER_CLIENT_ID, KROGER_CLIENT_SECRET, KROGER_TOKEN_URL, KROGER_API_BASE_URL


def getToken():
    payload = {
        'grant_type': 'client_credentials',
        'scope': 'product.compact'
    }
    client_auth = HTTPBasicAuth(KROGER_CLIENT_ID, KROGER_CLIENT_SECRET)
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    response = requests.post(KROGER_TOKEN_URL, auth=client_auth, data=payload, headers=headers)
    token_data = response.json()
    token = token_data.get('access_token')

    return token

def getProduct(product, locationId, token):
    filters= f'filter.locationId={locationId}&filter.term={product}'
    headers = {'Accept': 'application/json', 'Authorization': f'Bearer {token}'}
    response = requests.get(KROGER_API_BASE_URL + '/products?' + filters, headers=headers)
    product_data = response.json()

    return product_data

def getLocations(zipCode, token):
    filters = f'filter.zipCode.near={zipCode}&filter.radiusInMiles=100'
    headers = {'Accept': 'application/json', 'Authorization': f'Bearer {token}'}
    response = requests.get(KROGER_API_BASE_URL + '/locations?' + filters, headers=headers)
    location_data = response.json()
    locations_list = location_data['data']
    location_ids = [location['locationId'] for location in locations_list]

    return location_ids