import json

from src.prompts import build_grounded_prompt


def build_analytics_context(analytics_result):
    """Convert deterministic analytics results into grounded context."""

    return json.dumps(
        analytics_result,
        indent=2,
        ensure_ascii=False,
    )


def build_grounded_query(user_question, analytics_result):
    """Build a grounded prompt from verified analytics results."""

    analytics_context = build_analytics_context(analytics_result)

    return build_grounded_prompt(
        user_question=user_question,
        analytics_context=analytics_context,
    )