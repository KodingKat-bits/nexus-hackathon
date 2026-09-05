from src.analytics import (
    find_product_and_store,
    get_inventory_risks,
    get_non_moving_products,
    get_product_summary,
    get_sales_anomalies,
    get_stockout_risks,
)
from src.gemini_client import generate_response
from src.grounding import build_grounded_query
from src.router import detect_intent
from src.retrieval import load_index, retrieve

RETRIEVAL_INDEX = load_index()

def answer_question(user_question):
    """Route a user question to the appropriate deterministic analytics."""

    intent = detect_intent(user_question)

    if intent == "inventory":
        analytics_result = get_inventory_risks()

    elif intent == "sales_anomaly":
        analytics_result = get_sales_anomalies()

    elif intent == "stockout_risk":
        analytics_result = get_stockout_risks()

    elif intent == "non_moving":
        analytics_result = get_non_moving_products()

    elif intent == "product_performance":
        product_info = None

        from src.database import DB_PATH
        import sqlite3

        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()

        products = [
            row[0]
            for row in cursor.execute(
                "SELECT product_name FROM products"
            )
        ]

        stores = [
            row[0]
            for row in cursor.execute(
                "SELECT store_name FROM stores"
            )
        ]

        connection.close()

        question_lower = user_question.lower()

        matched_product = next(
            (
                product
                for product in products
                if product.lower() in question_lower
            ),
            None,
        )

        matched_store = next(
            (
                store
                for store in stores
                if store.lower() in question_lower
            ),
            None,
        )

        if matched_product and matched_store:
            product_info = find_product_and_store(
                product_name=matched_product,
                store_name=matched_store,
            )

        if product_info is None:
            return (
                "I could not identify the requested product and store. "
                "Please specify both."
            )

        analytics_result = get_product_summary(
            product_id=product_info["product_id"],
            store_id=product_info["store_id"],
        )
    else:
        return (
            "I can currently answer questions about inventory attention, "
            "non-moving products, and product performance."
        )

    try:
        retrieved_sections = retrieve(
            user_question,
            RETRIEVAL_INDEX,
            top_k=2,
        )
    except Exception:
        retrieved_sections = []

    if retrieved_sections:
        retrieved_context = "\n\n".join(
            f"{item['title']}:\n{item['text']}"
            for item in retrieved_sections
        )
    else:
        retrieved_context = (
            "No matching business-rule context was available. "
            "Do not infer business rules beyond the verified analytics."
        )

    grounded_prompt = build_grounded_query(
        user_question=user_question,
        analytics_result=analytics_result,
        retrieved_context=retrieved_context,
    )

    try:
        return generate_response(grounded_prompt)
    except Exception:
        return (
            "I’m unable to generate a response right now because the "
            "AI service is temporarily unavailable. Please try again."
        )


def answer_inventory_question(user_question):
    """Backward-compatible inventory question handler."""
    return answer_question(user_question)