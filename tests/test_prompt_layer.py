from src.prompts import build_grounded_prompt


def main():
    question = "Which product sold the most?"
    
    analytics_context = """
Product: Wireless Mouse
Units sold: 142
Revenue: ₹21,300

Product: Keyboard
Units sold: 97
Revenue: ₹19,400
"""

    prompt = build_grounded_prompt(
        user_question=question,
        analytics_context=analytics_context,
    )

    print(prompt)
    print("\nPrompt layer test OK")


if __name__ == "__main__":
    main()