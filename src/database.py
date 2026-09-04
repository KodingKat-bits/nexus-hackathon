import sqlite3
from pathlib import Path


# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Database location
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "retail.db"


def get_connection():
    """Create and return a connection to the SQLite database."""
    DATA_DIR.mkdir(exist_ok=True)
    return sqlite3.connect(DB_PATH)


def create_tables():
    """Create all required database tables."""
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stores (
            store_id INTEGER PRIMARY KEY,
            store_name TEXT NOT NULL,
            city TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY,
            product_name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
            store_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            sale_date TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            revenue REAL NOT NULL,
            FOREIGN KEY (store_id) REFERENCES stores(store_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            store_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            current_stock INTEGER NOT NULL,
            reorder_level INTEGER NOT NULL,
            PRIMARY KEY (store_id, product_id),
            FOREIGN KEY (store_id) REFERENCES stores(store_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        )
    """)

    connection.commit()
    connection.close()


if __name__ == "__main__":
    create_tables()
    print(f"Database created at: {DB_PATH}")