TRACK_ID=PS03

# NexusMart Retail Sales and Inventory Copilot

A grounded GenAI copilot for **NexusMart**, a fictional retail business. The application helps managers understand sales and inventory conditions using plain-language questions and provides data-backed recommendations.

## What the application does

The copilot can answer manager questions about:

* Inventory requiring attention
* Products at risk of future stockouts
* Non-moving products
* Sales spikes and drops
* Product performance and trends
* Product and store summaries

For inventory-related questions, the application can identify conditions such as:

* OUT_OF_STOCK
* LOW_STOCK
* OVERSTOCK
* NORMAL

The application also provides the relevant numbers, recommended action, and assumptions behind recommendations where supported by the available data.

If the available data cannot reliably answer a question, the system is designed to say so rather than guess.

## Architecture

The application follows a grounded analytics and retrieval architecture:

```text
SQLite database
      â†“
Deterministic Python analytics/business logic
      â†“
Structured factual results
      â†“
Local business-rule retrieval
(Gemini embeddings + cosine similarity)
      â†“
Grounding / business semantics
      â†“
Gemini
      â†“
Streamlit UI
```

The separation between analytics and language generation is intentional.

**SQLite and deterministic Python determine business facts. Gemini does not query the database and does not determine business numbers.** Gemini receives verified analytics context and relevant business-rule context and is used to explain the results naturally.

A small project-owned business-rules document is embedded using Gemini's `gemini-embedding-001` model. Relevant sections are retrieved locally using cosine similarity and supplied as business-rule context.

The retrieved document provides business semantics only. SQLite and deterministic Python analytics remain the source of truth for all business numbers and factual results.

This prevents the language model from inventing products, quantities, trends, or unsupported business conclusions.

## Data

The project uses a synthetic NexusMart retail dataset generated for the hackathon.

Current dataset:

* 3 stores
* 30 products
* 8,100 sales records
* 90 inventory records
* Sales period: 2026-06-06 to 2026-09-03

No external business data or external data service is required.

The project also includes a small synthetic business-rules document:

* `data/nexusmart_business_rules.md`
* Precomputed Gemini embeddings in `data/nexusmart_business_rules_embeddings.json`

The embedding index is committed to the repository so a fresh clone does not need to build the document index at startup.

## Running the application

### Requirements

* Python 3.11 recommended
* A Gemini API key available through the `GEMINI_API_KEY` environment variable

### Install dependencies

```bash
pip install -r requirements.txt
```

### Start the application

```bash
python app.py
```

Then open:

```text
http://localhost:8000
```

The project is designed for the hackathon judge workflow:

```text
pip install -r requirements.txt
python app.py
```

No separate frontend build or second terminal is required.

## Gemini configuration

Set the API key using the environment variable:

```text
GEMINI_API_KEY
```

The application uses Gemini for:

* Natural-language explanation of verified analytics
* Embeddings using `gemini-embedding-001` for business-rule retrieval

Gemini does not directly query SQLite and does not determine business numbers. Retrieval provides relevant business-rule context, while deterministic analytics remains the source of truth.

## Project structure

```text
app.py
requirements.txt
README.md

src/
    database.py
    analytics.py
    gemini_client.py
    prompts.py
    grounding.py
    copilot.py
    router.py
    retrieval.py

tests/
    test_prompt_layer.py
    test_grounding.py

data/
    retail.db
    nexusmart_business_rules.md
    nexusmart_business_rules_embeddings.json
```

## Validation

The project includes tests for important grounding and prompt-layer behavior.

The deterministic analytics layer has also been audited against the generated dataset, including:

* Inventory records: 90
* Non-moving products: 1
* Sales anomalies: 9
* Stockout risks: 47

Current stockout-risk results include:

* 16 HIGH-risk items, estimated to stock out within 3 days
* 31 MEDIUM-risk items, estimated to stock out within 5 days

Current out-of-stock items are excluded from future stockout prediction because they have already stocked out.

The application and retrieval pipeline have also been validated with the local embedding index and Gemini API.

## Failure handling

The application is designed to fail gracefully when external AI services are temporarily unavailable.

- Gemini generation failures return a user-friendly temporary-unavailable message.
- Gemini embedding/retrieval failures do not crash the application; the system continues without retrieved business-rule context.
- When business-rule context is unavailable, the grounding layer instructs the model not to infer unsupported business rules.
- Unsupported questions are routed away from deterministic analytics instead of producing fabricated business results.

## Hackathon compliance

The implementation is designed around the PS03 requirements:

* Plain-language manager questions
* Actual numbers behind answers
* Future stockout-risk detection
* Non-moving stock detection
* Sales spike/drop detection
* Identification of items requiring attention
* Recommended actions
* Data and assumptions behind recommendations
* Explicit handling of insufficient data instead of guessing
* Grounded GenAI
* Gemini embeddings for business-rule retrieval
* Project-owned business-rule document
* Precomputed local embedding index
* Local cosine-similarity retrieval
* Clear deterministic-logic / LLM separation
* Modular Python implementation
* Single-command application startup
* Synthetic/generated project data
* Gemini API through `GEMINI_API_KEY`

## Demo

Demo video:

`[Add final demo video link here]`

The final submission should replace the placeholder above with the submitted demo video URL.

## Project status

This repository contains the final hackathon application and its deterministic analytics, business-rule retrieval layer, grounding, Gemini explanation layer, tests, generated dataset, and Streamlit interface.