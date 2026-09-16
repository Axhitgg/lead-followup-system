# Service Business Lead Follow-up System

[![Lead API Tests](https://github.com/Axhitgg/lead-followup-system/actions/workflows/tests.yml/badge.svg)](https://github.com/Axhitgg/lead-followup-system/actions/workflows/tests.yml)

An AI-assisted intake system for small service businesses. It receives potential customer leads, classifies the requested service and urgency, recommends a follow-up action, stores the result, and prevents duplicate processing.

## Architecture

n8n Webhook → Flask API → OpenAI → PostgreSQL → JSON response

## Features

- Validates lead information
- Normalizes email addresses
- Requires an API key
- Prevents duplicate lead IDs
- Classifies service and urgency with OpenAI
- Recommends a next action
- Stores leads in PostgreSQL
- Provides health and readiness endpoints
- Runs with Docker Compose
- Includes automated tests and CI
- Includes Postman and n8n workflow exports

## Required lead fields

    {
      "lead_id": "lead-001",
      "name": "Anika",
      "email": "anika@example.com",
      "service": "Website redesign",
      "message": "I need a quote for redesigning my business website."
    }

## Example result

    {
      "received": true,
      "saved": true,
      "lead": {
        "lead_id": "lead-001",
        "service_category": "Website redesign / Web design",
        "urgency": "Medium",
        "next_action": "Schedule a discovery call"
      }
    }

## Run with Docker Compose

Create a local `.env` file with:

    OPENAI_API_KEY=your-local-key
    LEAD_API_KEY=lead-demo-key-2026
    POSTGRES_PASSWORD=local-password

Start the system:

    docker compose up --build -d

Check health:

    curl http://127.0.0.1:5060/health

Stop the system:

    docker compose down

## Test locally

    source ~/ai-automation-venv/bin/activate
    pytest -q

## Included files

- `lead_api.py` — Flask API
- `init.sql` — PostgreSQL schema
- `docker-compose.yml` — API and database services
- `lead_followup_n8n.json` — n8n workflow export
- `postman_collection.json` — Postman requests
- `test_lead_api.py` — automated tests
- `openapi.yml` — API contract

## Security

Secrets are stored in environment variables and are excluded from Git.
