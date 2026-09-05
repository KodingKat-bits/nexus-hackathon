import json

from src.prompts import build_grounded_prompt


def build_analytics_context(analytics_result):
    """Convert deterministic analytics results into grounded context."""

    business_rules = {
        "OUT_OF_STOCK": {
            "meaning": "product currently has no stock",
            "action": "replenish immediately",
            "assumption": "current stock status is directly observed from inventory data",
        },
        "LOW_STOCK": {
            "meaning": "product stock is at or below its reorder level",
            "action": "prioritize replenishment",
            "assumption": "reorder level is the inventory threshold defined in the dataset",
        },
        "OVERSTOCK": {
            "meaning": "product stock is at least 5 times its reorder level",
            "action": "review excess inventory before ordering more",
            "assumption": "the 5x reorder-level threshold is the business rule used to flag excess inventory",
        },
        "NORMAL": {
            "meaning": "inventory is neither low nor overstocked",
            "action": "no immediate inventory action",
            "assumption": "the defined inventory thresholds are appropriate for this analysis",
        },
        "HIGH": {
            "meaning": "high stockout risk; estimated stockout within 3 days",
            "action": "prioritize replenishment urgently",
            "assumption": "recent average daily sales continue at approximately the observed rate",
        },
        "MEDIUM": {
            "meaning": "medium stockout risk; estimated stockout within 5 days",
            "action": "plan replenishment soon",
            "assumption": "recent average daily sales continue at approximately the observed rate",
        },
    }

    context = {
        "inventory_business_rules": business_rules,
        "analytics_results": analytics_result,
    }

    return json.dumps(
        context,
        indent=2,
        ensure_ascii=False,
    )


def build_grounded_query(user_question, analytics_result, retrieved_context="",):
    """Build a grounded prompt from verified analytics results."""

    analytics_context = build_analytics_context(analytics_result)

    return build_grounded_prompt(user_question=user_question, analytics_context=analytics_context, retrieved_context=retrieved_context,)