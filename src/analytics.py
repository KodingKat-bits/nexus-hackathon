import sqlite3

from src.database import DB_PATH


def get_inventory_risks():
    """Return inventory items that need attention."""

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            i.store_id,
            s.store_name,
            i.product_id,
            p.product_name,
            p.category,
            i.current_stock,
            i.reorder_level
        FROM inventory i
        JOIN stores s
            ON i.store_id = s.store_id
        JOIN products p
            ON i.product_id = p.product_id
        ORDER BY i.current_stock ASC
    """)

    rows = cursor.fetchall()
    connection.close()

    results = []

    for row in rows:
        current_stock = row["current_stock"]
        reorder_level = row["reorder_level"]

        if current_stock == 0:
            status = "OUT_OF_STOCK"
            attention_type = "REPLENISHMENT"
        elif current_stock <= reorder_level:
            status = "LOW_STOCK"
            attention_type = "REPLENISHMENT"
        elif current_stock >= reorder_level * 5:
            status = "OVERSTOCK"
            attention_type = "EXCESS_INVENTORY"
        else:
            status = "NORMAL"
            attention_type = "NONE"

        results.append({
            "store_id": row["store_id"],
            "store_name": row["store_name"],
            "product_id": row["product_id"],
            "product_name": row["product_name"],
            "category": row["category"],
            "current_stock": current_stock,
            "reorder_level": reorder_level,
            "status": status,
            "attention_type": attention_type,
        })

    return results

def get_stockout_risks():
    """Identify products that may run out of stock based on recent sales."""

    inventory_items = get_inventory_risks()
    results = []

    for item in inventory_items:

        if item["current_stock"] == 0:
            continue
        trend = get_product_trend(
            item["product_id"],
            item["store_id"]
        )

        recent_average = trend.get("recent_average_daily_sales")

        if recent_average is None or recent_average <= 0:
            continue

        days_of_stock = item["current_stock"] / recent_average

        if days_of_stock <= 3:
            risk_level = "HIGH"
        elif days_of_stock <= 5:
            risk_level = "MEDIUM"
        else:
            continue

        results.append({
            "store_id": item["store_id"],
            "store_name": item["store_name"],
            "product_id": item["product_id"],
            "product_name": item["product_name"],
            "current_stock": item["current_stock"],
            "recent_average_daily_sales": recent_average,
            "estimated_days_until_stockout": round(days_of_stock, 1),
            "risk_level": risk_level,
        })

    results.sort(key=lambda x: x["estimated_days_until_stockout"])

    return results

def get_product_trend(product_id, store_id, days=30):
    """Compare recent sales with the previous period."""

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            sale_date,
            quantity
        FROM sales
        WHERE product_id = ?
          AND store_id = ?
        ORDER BY sale_date DESC
    """, (product_id, store_id))

    rows = cursor.fetchall()
    connection.close()

    if not rows:
        return {
            "product_id": product_id,
            "store_id": store_id,
            "trend": "NO_DATA",
        }

    recent_rows = rows[:days]
    previous_rows = rows[days:days * 2]

    if not previous_rows:
        return {
            "product_id": product_id,
            "store_id": store_id,
            "trend": "INSUFFICIENT_DATA",
        }

    recent_avg = sum(row["quantity"] for row in recent_rows) / len(recent_rows)
    previous_avg = sum(row["quantity"] for row in previous_rows) / len(previous_rows)

    if previous_avg == 0:
        if recent_avg > 0:
            trend = "INCREASING"
        else:
            trend = "NON_MOVING"
        change_percent = None
    else:
        change_percent = ((recent_avg - previous_avg) / previous_avg) * 100

        if change_percent > 10:
            trend = "INCREASING"
        elif change_percent < -10:
            trend = "DECLINING"
        else:
            trend = "STABLE"

    return {
        "product_id": product_id,
        "store_id": store_id,
        "recent_average_daily_sales": round(recent_avg, 2),
        "previous_average_daily_sales": round(previous_avg, 2),
        "change_percent": (
            round(change_percent, 2)
            if change_percent is not None
            else None
        ),
        "trend": trend,
    }


def get_non_moving_products(days=30):
    """Return products with no units sold during the given period."""

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            p.product_id,
            p.product_name,
            p.category,
            s.store_id,
            s.store_name,
            COALESCE(SUM(sa.quantity), 0) AS units_sold
        FROM inventory i
        JOIN products p
            ON i.product_id = p.product_id
        JOIN stores s
            ON i.store_id = s.store_id
        LEFT JOIN sales sa
            ON sa.product_id = i.product_id
            AND sa.store_id = i.store_id
            AND sa.sale_date >= date('now', ?)
        GROUP BY
            p.product_id,
            p.product_name,
            p.category,
            s.store_id,
            s.store_name
        HAVING units_sold = 0
        ORDER BY p.product_id
    """, (f"-{days} days",))

    rows = cursor.fetchall()
    connection.close()

    results = []

    for row in rows:
        results.append({
            "product_id": row["product_id"],
            "product_name": row["product_name"],
            "category": row["category"],
            "store_id": row["store_id"],
            "store_name": row["store_name"],
            "units_sold": row["units_sold"],
        })

    return results


def get_product_summary(product_id, store_id):
    """Return a complete performance summary for one product at one store."""

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            p.product_id,
            p.product_name,
            p.category,
            p.price,
            s.store_id,
            s.store_name,
            i.current_stock,
            i.reorder_level
        FROM products p
        JOIN inventory i
            ON p.product_id = i.product_id
        JOIN stores s
            ON i.store_id = s.store_id
        WHERE p.product_id = ?
          AND s.store_id = ?
    """, (product_id, store_id))

    product = cursor.fetchone()

    if not product:
        connection.close()
        return None

    cursor.execute("""
        SELECT
            COALESCE(SUM(quantity), 0) AS total_units_sold,
            COALESCE(SUM(revenue), 0) AS total_revenue
        FROM sales
        WHERE product_id = ?
          AND store_id = ?
    """, (product_id, store_id))

    totals = cursor.fetchone()

    connection.close()

    trend = get_product_trend(product_id, store_id)

    return {
        "product_id": product["product_id"],
        "product_name": product["product_name"],
        "category": product["category"],
        "price": product["price"],
        "store_id": product["store_id"],
        "store_name": product["store_name"],
        "current_stock": product["current_stock"],
        "reorder_level": product["reorder_level"],
        "total_units_sold": totals["total_units_sold"],
        "total_revenue": round(totals["total_revenue"], 2),
        "recent_average_daily_sales": trend.get(
            "recent_average_daily_sales"
        ),
        "previous_average_daily_sales": trend.get(
            "previous_average_daily_sales"
        ),
        "change_percent": trend.get("change_percent"),
        "trend": trend.get("trend"),
    }

def find_product_and_store(product_name, store_name):
    """Find product and store IDs using exact names."""

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("""
        SELECT product_id
        FROM products
        WHERE LOWER(product_name) = LOWER(?)
    """, (product_name,))

    product = cursor.fetchone()

    cursor.execute("""
        SELECT store_id
        FROM stores
        WHERE LOWER(store_name) = LOWER(?)
    """, (store_name,))

    store = cursor.fetchone()

    connection.close()

    if not product or not store:
        return None

    return {
        "product_id": product["product_id"],
        "store_id": store["store_id"],
    }


def get_sales_anomalies():
    """Identify significant sales increases and decreases."""

    from src.database import DB_PATH
    import sqlite3

    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    products = dict(
        cursor.execute(
            "SELECT product_id, product_name FROM products"
        ).fetchall()
    )

    stores = dict(
        cursor.execute(
            "SELECT store_id, store_name FROM stores"
        ).fetchall()
    )

    connection.close()

    anomalies = []

    for product_id in range(1, 31):
        for store_id in range(1, 4):
            trend = get_product_trend(product_id, store_id)

            change_percent = trend.get("change_percent")

            if change_percent is None:
                continue

            if change_percent >= 15:
                anomaly_type = "SALES_SPIKE"
            elif change_percent <= -15:
                anomaly_type = "SALES_DROP"
            else:
                continue

            anomalies.append(
                {
                    "product_id": product_id,
                    "product_name": products[product_id],
                    "store_id": store_id,
                    "store_name": stores[store_id],
                    "change_percent": change_percent,
                    "trend": trend["trend"],
                    "anomaly_type": anomaly_type,
                }
            )

    return anomalies