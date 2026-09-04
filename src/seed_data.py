import sqlite3
import random
from datetime import date, timedelta
from pathlib import Path

from database import DB_PATH


random.seed(42)


STORES = [
    (1, "NexusMart Hyderabad Central", "Hyderabad"),
    (2, "NexusMart Secunderabad", "Secunderabad"),
    (3, "NexusMart Gachibowli", "Hyderabad"),
]


PRODUCTS = [
    (1, "Basmati Rice 5kg", "Grocery", 520.0),
    (2, "Wheat Flour 5kg", "Grocery", 280.0),
    (3, "Cooking Oil 1L", "Grocery", 145.0),
    (4, "Sugar 1kg", "Grocery", 52.0),
    (5, "Toor Dal 1kg", "Grocery", 165.0),
    (6, "Tea 500g", "Grocery", 240.0),
    (7, "Coffee 200g", "Grocery", 190.0),
    (8, "Biscuits Pack", "Snacks", 40.0),
    (9, "Potato Chips", "Snacks", 30.0),
    (10, "Chocolate Bar", "Snacks", 50.0),

    (11, "Shampoo 650ml", "Personal Care", 310.0),
    (12, "Bath Soap Pack", "Personal Care", 180.0),
    (13, "Toothpaste 200g", "Personal Care", 125.0),
    (14, "Face Wash 100ml", "Personal Care", 220.0),
    (15, "Laundry Detergent 2kg", "Home Care", 260.0),
    (16, "Dishwash Liquid 500ml", "Home Care", 110.0),
    (17, "Floor Cleaner 1L", "Home Care", 150.0),
    (18, "Tissue Box", "Home Care", 95.0),

    (19, "Mineral Water 1L", "Beverages", 25.0),
    (20, "Orange Juice 1L", "Beverages", 130.0),
    (21, "Cola 750ml", "Beverages", 55.0),
    (22, "Energy Drink", "Beverages", 120.0),
    (23, "Milk 1L", "Dairy", 65.0),
    (24, "Curd 500g", "Dairy", 45.0),
    (25, "Cheese 200g", "Dairy", 180.0),

    (26, "Notebook", "Stationery", 70.0),
    (27, "Ball Pen Pack", "Stationery", 60.0),
    (28, "LED Bulb", "Electronics", 140.0),
    (29, "Phone Charger", "Electronics", 450.0),
    (30, "AA Batteries Pack", "Electronics", 180.0),
]


# Product demand levels.
# Higher number = more units normally sold per day.
BASE_DEMAND = {
    1: 8, 2: 7, 3: 9, 4: 6, 5: 7,
    6: 5, 7: 4, 8: 12, 9: 10, 10: 8,
    11: 5, 12: 6, 13: 6, 14: 4, 15: 5,
    16: 4, 17: 3, 18: 3, 19: 18, 20: 7,
    21: 10, 22: 5, 23: 12, 24: 8, 25: 4,
    26: 5, 27: 7, 28: 3, 29: 2, 30: 3,
}


def clear_existing_data(connection):
    cursor = connection.cursor()

    cursor.execute("DELETE FROM sales")
    cursor.execute("DELETE FROM inventory")
    cursor.execute("DELETE FROM products")
    cursor.execute("DELETE FROM stores")

    connection.commit()


def insert_stores(connection):
    connection.executemany(
        """
        INSERT INTO stores (store_id, store_name, city)
        VALUES (?, ?, ?)
        """,
        STORES,
    )


def insert_products(connection):
    connection.executemany(
        """
        INSERT INTO products (product_id, product_name, category, price)
        VALUES (?, ?, ?, ?)
        """,
        PRODUCTS,
    )


def generate_sales():
    sales = []

    start_date = date.today() - timedelta(days=90)

    sale_id = 1

    for day_offset in range(90):
        current_date = start_date + timedelta(days=day_offset)

        for store_id, _, _ in STORES:
            for product_id, _, _, price in PRODUCTS:

                base = BASE_DEMAND[product_id]

                # Store-specific demand differences
                store_multiplier = {
                    1: 1.15,
                    2: 0.90,
                    3: 1.05,
                }[store_id]

                quantity = max(
                    0,
                    round(
                        random.gauss(
                            base * store_multiplier,
                            max(1, base * 0.25),
                        )
                    ),
                )

                # -----------------------------
                # DELIBERATE BUSINESS PATTERNS
                # -----------------------------

                # Product 7: declining sales at Store 2
                if product_id == 7 and store_id == 2 and day_offset > 60:
                    quantity = max(0, round(quantity * 0.35))

                # Product 10: sales spike at Store 1
                if product_id == 10 and store_id == 1 and 65 <= day_offset <= 72:
                    quantity *= 4

                # Product 20: sales drop at Store 3
                if product_id == 20 and store_id == 3 and day_offset > 65:
                    quantity = max(0, round(quantity * 0.30))

                # Product 26: non-moving product at Store 2
                if product_id == 26 and store_id == 2:
                    quantity = 0

                # Product 29: unusually strong demand at Store 1
                if product_id == 29 and store_id == 1 and 45 <= day_offset <= 55:
                    quantity *= 3

                revenue = quantity * price

                sales.append(
                    (
                        sale_id,
                        store_id,
                        product_id,
                        current_date.isoformat(),
                        quantity,
                        round(revenue, 2),
                    )
                )

                sale_id += 1

    return sales


def insert_sales(connection, sales):
    connection.executemany(
        """
        INSERT INTO sales
        (sale_id, store_id, product_id, sale_date, quantity, revenue)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        sales,
    )


def generate_inventory():
    inventory = []

    for store_id, _, _ in STORES:
        for product_id, _, _, _ in PRODUCTS:

            demand = BASE_DEMAND[product_id]

            # Normal stock based on roughly several days of demand
            stock = random.randint(
                max(1, demand * 2),
                max(2, demand * 8),
            )

            reorder_level = max(5, demand * 2)

            # --------------------------------
            # DELIBERATE INVENTORY CONDITIONS
            # --------------------------------

            # Stock-out
            if product_id == 3 and store_id == 1:
                stock = 0

            # Overstock
            if product_id == 17 and store_id == 2:
                stock = 150

            # Non-moving inventory
            if product_id == 26 and store_id == 2:
                stock = 80

            # Very low stock
            if product_id == 29 and store_id == 1:
                stock = 2

            inventory.append(
                (
                    store_id,
                    product_id,
                    stock,
                    reorder_level,
                )
            )

    return inventory


def insert_inventory(connection, inventory):
    connection.executemany(
        """
        INSERT INTO inventory
        (store_id, product_id, current_stock, reorder_level)
        VALUES (?, ?, ?, ?)
        """,
        inventory,
    )


def print_summary(connection):
    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM stores")
    print("Stores:", cursor.fetchone()[0])

    cursor.execute("SELECT COUNT(*) FROM products")
    print("Products:", cursor.fetchone()[0])

    cursor.execute("SELECT COUNT(*) FROM sales")
    print("Sales records:", cursor.fetchone()[0])

    cursor.execute("SELECT COUNT(*) FROM inventory")
    print("Inventory records:", cursor.fetchone()[0])


def main():
    print("Seeding NexusMart database...")

    connection = sqlite3.connect(DB_PATH)

    try:
        clear_existing_data(connection)

        insert_stores(connection)
        insert_products(connection)

        sales = generate_sales()
        insert_sales(connection, sales)

        inventory = generate_inventory()
        insert_inventory(connection, inventory)

        connection.commit()

        print("\nDatabase successfully populated.")
        print_summary(connection)

    finally:
        connection.close()


if __name__ == "__main__":
    main()