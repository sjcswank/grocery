import sqlite3

conn = sqlite3.connect('grocery.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    category TEXT,
    bought_count INTEGER DEFAULT 0
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS past_lists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_name TEXT NOT NULL,
    bought_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

conn.commit()
conn.close()


def add_item(name, category=None):
    conn = sqlite3.connect('grocery.db')
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO items (name, category) VALUES (?, ?)', (name, category))
        conn.commit()
        print(f"Item '{name}' added successfully.")
    except sqlite3.IntegrityError:
        print(f"Item '{name}' already exists.")
    conn.close()


def mark_as_bought(name):
    conn = sqlite3.connect('grocery.db')
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE items
        SET bought_count = bought_count + 1
        WHERE name = ?
    ''', (name,))

    cursor.execute('''
        INSERT INTO past_lists (item_name)
        VALUES (?)
    ''', (name,))

    conn.commit()
    print(f"Item '{name}' marked as bought.")
    conn.close()


def suggest_items(top_n=5):
    conn = sqlite3.connect('grocery.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT name, bought_count
        FROM items
        ORDER BY bought_caount DESC
        LIMIT ?
    ''', (top_n,))

    suggestions = cursor.fetchall()
    conn.close()

    print("Suggested Items:")
    for item in suggestions:
        print(f"- {item[0]} (bought {item[1]} times)")


def view_past_lists():
    conn = sqlite3.connect('grocery.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT item_name, bought_date
        FROM past_lists
        ORDER BY bought_date DESC
    ''')

    past_items = conn.fetchall()
    conn.close()

    print("Past Purchases:")
    for item in past_items:
        print(f"- {item[0]} (bought on {item[1]})")

