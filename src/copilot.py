from src.analytics import get_inventory_risks
from src.gemini_client import generate_response
from src.grounding import build_grounded_query


def answer_inventory_question(user_question):
    """Answer an inventory-related question using grounded analytics."""

    analytics_result = get_inventory_risks()

    grounded_prompt = build_grounded_query(
        user_question=user_question,
        analytics_result=analytics_result,
    )

    return generate_response(grounded_prompt)