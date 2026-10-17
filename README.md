# Lead Follow-up System

An AI-assisted lead intake prototype for service businesses, using n8n, Python, Flask, OpenAI and PostgreSQL. It organises enquiries and returns a suggested next step for follow-up.

## Business problem

Potential customers send requests with different levels of urgency. Reading every message manually can delay a useful response or leave an urgent enquiry unnoticed. This project classifies the enquiry and makes it available as a structured record for a follow-up workflow.

## Example

A customer asks for an urgent website repair. The API checks their details and lead ID, classifies service category and urgency, saves the result and returns a next-action suggestion. An n8n workflow can use that result to notify the business through Gmail. A suggestion is not proof that a customer was contacted.

```text
Customer -> n8n webhook -> Flask validation / duplicate check
         -> OpenAI classification -> Output checks -> PostgreSQL -> JSON
n8n -> Urgency-based follow-up / Gmail alert
```

## Features and included files

- Required lead fields, email normalisation and environment-based API-key checks.
- AI summary, service category, Low / Medium / High urgency and next action.
- AI required-field/urgency checks, PostgreSQL storage and local JSONL events.
- Docker Compose, automated tests and CI.
- `lead_followup_n8n.json`: workflow export; reconnect triggers, URLs and your own credentials after import.
- `postman_collection.json` and `openapi.yml`: request examples and API contract.

## Run locally

Create an untracked `.env` in the cloned repository:

```dotenv
OPENAI_API_KEY=replace-with-your-own-key
LEAD_API_KEY=replace-with-a-unique-local-secret
POSTGRES_PASSWORD=replace-with-a-url-safe-local-password
```

Docker Compose starts the API and PostgreSQL. Model calls can incur OpenAI charges.

```sh
docker compose up --build -d
curl http://127.0.0.1:5060/health
```

Compose supplies DATABASE_URL and uses `init.sql` to initialise a new database volume. Existing data is not automatically migrated. Stop without deleting data using `docker compose down`.

## API

| Method | Path | Purpose |
| --- | --- | --- |
| GET | /health | Process-health response |
| POST | /lead | Validate, classify and store an enquiry |

POST requires `X-API-Key` matching LEAD_API_KEY. Use synthetic data:

```json
{
  "lead_id": "demo-lead-001",
  "name": "Demo Customer",
  "email": "demo@example.com",
  "service": "Website support",
  "message": "Our website is down and we need help today."
}
```

Required fields are lead_id, name, email, service and message. Success returns `received`, `saved`, `database_id` and the classified `lead`. Missing fields and duplicate IDs currently return HTTP 200 with `received: false`; inspect the response body before routing. Classification failure returns HTTP 422 with `status: human_review`; it is not a successfully saved lead.

## Tests

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt pytest
python -m pytest -q test_lead_api.py
```

Four tests cover missing API key, missing email, a mocked successful classification/save, and duplicate lead ID. These do not establish AI accuracy or email delivery. [Inspect CI runs](https://github.com/Axhitgg/lead-followup-system/actions). No conversion-rate or response-time improvement has been measured.

## Security and limitations

The project is a portfolio prototype, not a CRM replacement or guaranteed follow-up service. AI urgency can be wrong; keep human oversight for consequential requests. Basic duplicate checks are not full concurrent idempotency. There is no durable email-delivery ledger. Health checks process availability only; the current lead API does not expose `/ready`. Customer text is sent to OpenAI, and `lead_audit.jsonl` can contain customer details. Keep secrets and logs outside Git and use fictional enquiries for demos. The API development entry point uses debug mode and is not a public production server.

## Author

[Akshit Singh](https://www.linkedin.com/in/akshit-singh-outlook/) - AI automation portfolio project.
