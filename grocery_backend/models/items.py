from ..config import DB_PATH
import sqlite3

def create_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        current INTEGER DEFAULT 0,
        bought INTEGER DEFAULT 0,
        total_purchases INTEGER DEFAULT 0,
        last_purchase_date TIMESTAMP,
        created_at TIMESTAMP
        )
    """
    )
    conn.commit()
    conn.close()