import json
import math
from pathlib import Path

from src.gemini_client import generate_embedding


DOCUMENT_PATH = Path("data/nexusmart_business_rules.md")
INDEX_PATH = Path("data/nexusmart_business_rules_embeddings.json")


def _split_document(text):
    """Split the business-rules document into searchable sections."""

    sections = []
    current_title = None
    current_lines = []

    for line in text.splitlines():
        if line.startswith("## "):
            if current_title and current_lines:
                sections.append(
                    {
                        "title": current_title,
                        "text": "\n".join(current_lines).strip(),
                    }
                )

            current_title = line[3:].strip()
            current_lines = []
        elif current_title:
            current_lines.append(line)

    if current_title and current_lines:
        sections.append(
            {
                "title": current_title,
                "text": "\n".join(current_lines).strip(),
            }
        )

    return sections


def _cosine_similarity(vector_a, vector_b):
    """Return cosine similarity between two embedding vectors."""

    dot_product = sum(a * b for a, b in zip(vector_a, vector_b))
    magnitude_a = math.sqrt(sum(a * a for a in vector_a))
    magnitude_b = math.sqrt(sum(b * b for b in vector_b))

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return dot_product / (magnitude_a * magnitude_b)


def build_index():
    """Build and persist embeddings for the local business-rules document."""

    text = DOCUMENT_PATH.read_text(encoding="utf-8")
    sections = _split_document(text)

    index = []

    for section in sections:
        embedding = generate_embedding(section["text"])

        index.append(
            {
                "title": section["title"],
                "text": section["text"],
                "embedding": embedding,
            }
        )

    INDEX_PATH.write_text(
        json.dumps(index),
        encoding="utf-8",
    )

    return index


def load_index():
    """Load the persisted local embedding index."""

    if not INDEX_PATH.exists():
        return build_index()

    return json.loads(
        INDEX_PATH.read_text(encoding="utf-8")
    )


def retrieve(query, index, top_k=2):
    """Return the most relevant document sections for a query."""

    query_embedding = generate_embedding(query)

    scored = []

    for item in index:
        score = _cosine_similarity(
            query_embedding,
            item["embedding"],
        )

        scored.append(
            {
                "title": item["title"],
                "text": item["text"],
                "score": score,
            }
        )

    scored.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    return scored[:top_k]