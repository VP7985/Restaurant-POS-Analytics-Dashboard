# utils/db_utils.py
import sqlite3
import pandas as pd
import os

DB_FILE = os.path.join('db', 'restaurant.db')

def _initialize_database():
    """Creates/updates the database and tables."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        
        # Menu Table with image_path
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS menu (
                id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE,
                category TEXT, price REAL, image_path TEXT
            )
        ''')
        
        # Orders Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY, order_type TEXT, payment_method TEXT, 
                subtotal REAL, discount REAL, gst REAL, total REAL, 
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Order Items Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY, order_id INTEGER, item_name TEXT, 
                quantity INTEGER, price_per_item REAL,
                FOREIGN KEY (order_id) REFERENCES orders(id)
            )
        ''')
        
        # Add image_path column if it doesn't exist (for migration)
        try:
            cursor.execute("SELECT image_path FROM menu LIMIT 1")
        except sqlite3.OperationalError:
            cursor.execute("ALTER TABLE menu ADD COLUMN image_path TEXT")

        # Check if menu is empty and add sample data
        cursor.execute("SELECT COUNT(*) FROM menu")
        if cursor.fetchone()[0] == 0:
            sample_menu = [
                (1, 'Margherita Pizza', 'Pizza', 450.00, 'assets/Margherita_Pizza.jpg'),
                (2, 'Pepperoni Feast', 'Pizza', 520.00, 'assets/Pepperoni_Feast.jpg'),
                (3, 'Classic Veg Burger', 'Burgers', 250.00, 'assets/Classic_Veg_Burger.jpg'),
                (4, 'Spicy Chicken Burger', 'Burgers', 280.00, 'assets/Spicy_Chicken_Burger.jpg'),
                (5, 'Cheesy Garlic Bread', 'Sides', 180.00, 'assets/Cheesy_Garlic_Bread.jpg'),
                (6, 'Coca-Cola', 'Beverages', 60.00, 'assets/Coca-Cola.jpg'),
                (7, 'Fresh Lime Soda', 'Beverages', 80.00, 'assets/Fresh_Lime_Soda.jpg')
            ]
            cursor.executemany("INSERT INTO menu (id, name, category, price, image_path) VALUES (?, ?, ?, ?, ?)", sample_menu)
        conn.commit()

_initialize_database()

def get_menu_from_db():
    with sqlite3.connect(DB_FILE) as conn:
        return pd.read_sql_query("SELECT id, name, category, price, image_path FROM menu ORDER BY category, name", conn)

def save_order_to_db(order_data):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        details = order_data['details']
        cursor.execute(
            'INSERT INTO orders (order_type, payment_method, subtotal, discount, gst, total) VALUES (?, ?, ?, ?, ?, ?)',
            (order_data['order_type'], order_data['payment_method'], details['subtotal'],
             details['discount'], details['gst'], details['total'])
        )
        order_id = cursor.lastrowid
        items_to_save = [(order_id, name, item_details['quantity'], item_details['price'])
                         for name, item_details in order_data['items'].items()]
        cursor.executemany('INSERT INTO order_items (order_id, item_name, quantity, price_per_item) VALUES (?, ?, ?, ?)', items_to_save)
        conn.commit()
        return order_id

def update_menu_from_csv(uploaded_file):
    try:
        df = pd.read_csv(uploaded_file)
        # Check for image_path, but make it optional
        required_cols = ['name', 'category', 'price']
        if not all(col in df.columns for col in required_cols):
            return False, "CSV must contain 'name', 'category', and 'price' columns."
        if 'image_path' not in df.columns:
            df['image_path'] = None # Add empty column if not present

        with sqlite3.connect(DB_FILE) as conn:
            conn.execute("DELETE FROM menu")
            df.to_sql('menu', conn, if_exists='append', index=False)
            conn.commit()
        return True, f"Successfully imported {len(df)} items."
    except Exception as e:
        return False, f"An error occurred: {e}"

def get_sales_report_from_db(period="Daily"):
    with sqlite3.connect(DB_FILE) as conn:
        formats = {"Daily": "'%Y-%m-%d'", "Weekly": "'%Y-W%W'", "Monthly": "'%Y-%m'"}
        period_format = formats.get(period, "'%Y-%m-%d'")
        
        sales_summary = pd.read_sql_query(
            f"SELECT strftime({period_format}, timestamp) as Period, COUNT(id) as 'Total Orders', SUM(total) as 'Total Sales' FROM orders GROUP BY Period ORDER BY Period DESC", conn
        )
        most_sold_items = pd.read_sql_query(
            "SELECT item_name as 'Item Name', SUM(quantity) as 'Quantity Sold' FROM order_items GROUP BY item_name ORDER BY `Quantity Sold` DESC LIMIT 10", conn
        )
        sales_by_category = pd.read_sql_query(
            "SELECT m.category as Category, SUM(oi.quantity) as 'Total Quantity' FROM order_items oi JOIN menu m ON oi.item_name = m.name GROUP BY Category", conn
        )
        sales_by_payment = pd.read_sql_query(
            "SELECT payment_method as 'Payment Method', COUNT(id) as 'Transaction Count' FROM orders GROUP BY `Payment Method`", conn
        )
    return sales_summary, most_sold_items, sales_by_category, sales_by_payment
