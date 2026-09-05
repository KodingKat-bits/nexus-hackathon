from src.analytics import (
    find_product_and_store,
    get_inventory_risks,
    get_non_moving_products,
    get_product_summary,
)
from src.gemini_client import generate_response
from src.grounding import build_grounded_query
from src.router import detect_intent


def answer_question(user_question):
    """Route a user question to the appropriate deterministic analytics."""

    intent = detect_intent(user_question)

    if intent == "inventory":
        analytics_result = get_inventory_risks()

    elif intent == "non_moving":
        analytics_result = get_non_moving_products()

    elif intent == "product_performance":
        product_info = find_product_and_store(
            product_name="Coffee 200g",
            store_name="NexusMart Gachibowli",
        )

        if product_info is None:
            return "I could not identify the requested product and store."

        analytics_result = get_product_summary(
            product_id=product_info["product_id"],
            store_id=product_info["store_id"],
        )

    else:
        return (
            "I can currently answer questions about inventory attention, "
            "non-moving products, and product performance."
        )

    grounded_prompt = build_grounded_query(
        user_question=user_question,
        analytics_result=analytics_result,
    )

    return generate_response(grounded_prompt)


def answer_inventory_question(user_question):
    """Backward-compatible inventory question handler."""
    return answer_question(user_question)