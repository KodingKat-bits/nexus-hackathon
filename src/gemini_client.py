import os

from google import genai


MODEL_NAME = "gemini-3.5-flash-lite"


def get_client():
    """Create and return a Gemini API client."""

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY environment variable is not set."
        )

    return genai.Client(api_key=api_key)


def generate_response(prompt):
    """Send a prompt to Gemini and return the text response."""

    client = get_client()

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
    )

    return response.text

def generate_embedding(text):
    """Generate a Gemini embedding for the supplied text."""

    client = get_client()

    response = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text,
    )

    return response.embeddings[0].values