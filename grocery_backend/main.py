from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime
from . import create_app
from .config import DB_PATH, DEBUG, PORT
from .models import items


def init_db():
    items.create_table()


# Create DB
init_db()

# Create App
app = create_app()

if __name__ == '__main__':
    app.run(debug=DEBUG, port=PORT)
