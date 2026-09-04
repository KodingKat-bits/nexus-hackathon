from src.grounding import build_grounded_query


def main():
    analytics_result = [
        {
            "product_name": "Wireless Mouse",
            "current_stock": 8,
            "reorder_level": 10,
            "status": "LOW_STOCK",
        },
        {
            "product_name": "Keyboard",
            "current_stock": 50,
            "reorder_level": 10,
            "status": "NORMAL",
        },
    ]

    prompt = build_grounded_query(
        user_question="Which products need attention?",
        analytics_result=analytics_result,
    )

    print(prompt)
    print("\nGrounding layer test OK")


if __name__ == "__main__":
    main()