def detect_intent(user_question):
    """Determine which deterministic analytics capability should handle a question."""

    question = user_question.lower().strip()

    if any(word in question for word in [
        "inventory",
        "low stock",
        "overstock",
        "replenishment",
    ]):
        return "inventory"

    if any(word in question for word in [
        "not moving",
        "non-moving",
        "non moving",
        "no sales",
    ]):
        return "non_moving"
    
    if any(word in question for word in [
    "stockout",
    "stock out",
    "run out",
    "running out",
    "stockout risk",
    ]):
        return "stockout_risk"
    
    if any(word in question for word in [
    "spike",
    "spikes",
    "drop",
    "drops",
    "unusual sales",
    "sales anomaly",
    "sales anomalies",
    "sudden increase",
    "sudden decrease",
    ]):
        return "sales_anomaly"

    if any(word in question for word in [
        "trend",
        "performance",
        "sold",
        "sales",
        "revenue",
        "performing",
        "product",
    ]):
        return "product_performance"

    return "unknown"