import sqlite3

def format_price(price):
    try:
        # Try to convert the price to float and format it
        return f"{float(price):,.2f}"
    except (ValueError, TypeError):
        # If conversion fails, return the original string
        return str(price)

def setup_database():
    conn = sqlite3.connect('watches.db')
    cursor = conn.cursor()
    
    # Check if the table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='watches'")
    table_exists = cursor.fetchone() is not None

    if not table_exists:
        # If the table doesn't exist, create it with all columns
        cursor.execute('''
        CREATE TABLE watches (
            product_id TEXT PRIMARY KEY,
            brand TEXT,
            model TEXT,
            ref TEXT,
            price REAL,
            currency TEXT,
            condition TEXT,
            year TEXT
        )
        ''')
    else:
        # If the table exists, check if all columns are present
        cursor.execute("PRAGMA table_info(watches)")
        columns = [column[1] for column in cursor.fetchall()]
        expected_columns = ['product_id', 'brand', 'model', 'ref', 'price', 'currency', 'condition', 'year']
        
        for column in expected_columns:
            if column not in columns:
                cursor.execute(f'ALTER TABLE watches ADD COLUMN {column} TEXT')
        
        # Remove the first_seen_date column if it exists
        if 'first_seen_date' in columns:
            cursor.execute('CREATE TABLE watches_new AS SELECT product_id, brand, model, ref, price, currency, condition, year FROM watches')
            cursor.execute('DROP TABLE watches')
            cursor.execute('ALTER TABLE watches_new RENAME TO watches')
    
    conn.commit()
    return conn

def insert_watch(conn, watch_data):
    cursor = conn.cursor()
    cursor.execute('''
    INSERT OR REPLACE INTO watches 
    (product_id, brand, model, ref, price, currency, condition, year)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', watch_data)
    conn.commit()

def update_watch(conn, watch_data):
    cursor = conn.cursor()
    cursor.execute('''
    UPDATE watches 
    SET brand = ?, model = ?, ref = ?, price = ?, currency = ?, condition = ?, year = ?
    WHERE product_id = ?
    ''', (*watch_data[1:], watch_data[0]))
    conn.commit()

def check_watch_exists(conn, product_id):
    cursor = conn.cursor()
    cursor.execute("SELECT product_id FROM watches WHERE product_id = ?", (product_id,))
    return cursor.fetchone() is not None

def query_watches(conn, brand=None, model=None, condition=None, ref=None, year=None):
    cursor = conn.cursor()
    
    query = "SELECT * FROM watches WHERE 1=1"
    params = []

    if brand and brand != "All Brands":
        query += " AND brand LIKE ?"
        params.append(f"%{brand}%")
    
    if model and model != "All Models":
        query += " AND model LIKE ?"
        params.append(f"%{model}%")
    
    if condition and condition != "All Conditions":
        query += " AND condition LIKE ?"
        params.append(f"%{condition}%")

    if ref and ref != "All References":
        query += " AND ref LIKE ?"
        params.append(f"%{ref}%")

    if year and year != "All Years":
        query += " AND year LIKE ?"
        params.append(f"%{year}%")

    cursor.execute(query, params)
    return cursor.fetchall()

def clear_database(conn):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM watches")
    conn.commit()
    print("Database cleared.")

def get_all_watches(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM watches")
    return cursor.fetchall()

def get_unique_values(conn, column):
    cursor = conn.cursor()
    cursor.execute(f"SELECT DISTINCT {column} FROM watches WHERE {column} IS NOT NULL AND {column} != ''")
    return [row[0] for row in cursor.fetchall()]

def test_watch_data(watch_data):
    if len(watch_data) != 8:
        print("Error: Incorrect number of data fields.")
        return

    fields = ['Product ID', 'Brand', 'Model', 'Reference', 'Price', 'Currency', 'Condition', 'Year']
    
    print("Test Watch Data:")
    print("-----------------")
    for field, value in zip(fields, watch_data):
        print(f"{field}: {value}")
    print("-----------------")

    try:
        price = float(watch_data[4])
        print(f"Price (as float): {price}")
    except ValueError:
        print("Warning: Price is not a valid float.")

    if not watch_data[3]:
        print("Warning: Reference (SKU) is empty.")

    if not watch_data[7]:
        print("Warning: Year is empty.")

        # Add this function to database.py

def get_watch_statistics(conn, brand=None, model=None, condition=None, ref=None, year=None):
    cursor = conn.cursor()
    
    query = "SELECT price FROM watches WHERE 1=1"
    params = []

    if brand and brand != "All Brands":
        query += " AND brand LIKE ?"
        params.append(f"%{brand}%")
    
    if model and model != "All Models":
        query += " AND model LIKE ?"
        params.append(f"%{model}%")
    
    if condition and condition != "All Conditions":
        query += " AND condition LIKE ?"
        params.append(f"%{condition}%")

    if ref and ref != "All References":
        query += " AND ref LIKE ?"
        params.append(f"%{ref}%")

    if year and year != "All Years":
        query += " AND year LIKE ?"
        params.append(f"%{year}%")

    cursor.execute(query, params)
    prices = [row[0] for row in cursor.fetchall() if row[0] is not None]
    
    if not prices:
        return None, None, None

    avg_price = sum(prices) / len(prices)
    max_price = max(prices)
    min_price = min(prices)

    return format_price(avg_price), format_price(max_price), format_price(min_price)

# Add this new function to database.py

def get_filtered_values(conn, column, brand=None, model=None, condition=None, ref=None, year=None):
    cursor = conn.cursor()
    
    query = f"SELECT DISTINCT {column} FROM watches WHERE {column} IS NOT NULL AND {column} != ''"
    params = []

    if brand and brand != "All Brands":
        query += " AND brand LIKE ?"
        params.append(f"%{brand}%")
    
    if model and model != "All Models":
        query += " AND model LIKE ?"
        params.append(f"%{model}%")
    
    if condition and condition != "All Conditions":
        query += " AND condition LIKE ?"
        params.append(f"%{condition}%")

    if ref and ref != "All References":
        query += " AND ref LIKE ?"
        params.append(f"%{ref}%")

    if year and year != "All Years":
        query += " AND year LIKE ?"
        params.append(f"%{year}%")

    cursor.execute(query, params)
    return [row[0] for row in cursor.fetchall()]