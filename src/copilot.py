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

    else:
        return (
            "I can currently answer questions about inventory attention "
            "and non-moving products. Please ask one of those questions."
        )

    grounded_prompt = build_grounded_query(
        user_question=user_question,
        analytics_result=analytics_result,
    )

    return generate_response(grounded_prompt)


def answer_inventory_question(user_question):
    """Backward-compatible inventory question handler."""
    return answer_question(user_question)