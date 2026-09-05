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

The application follows a grounded analytics architecture:

```text
SQLite database
      ↓
Deterministic Python analytics/business logic
      ↓
Structured factual results
      ↓
Grounding / business semantics
      ↓
Gemini
      ↓
Streamlit UI
```

The separation between analytics and language generation is intentional.

**SQLite and Python determine business facts. Gemini does not query the database and does not determine business numbers.** Gemini receives verified analytics context and is used to explain the results naturally.

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

## Running the application

### Requirements

* Python 3.10+ recommended
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

The application uses Gemini for natural-language explanation after deterministic analytics have produced verified results.

The application does not use Gemini to directly query SQLite.

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

tests/
    test_prompt_layer.py
    test_grounding.py

data/
    retail.db
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

This repository contains the final hackathon application and its deterministic analytics, grounding, Gemini explanation layer, tests, generated dataset, and Streamlit interface.
