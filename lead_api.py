from flask import Flask, request, jsonify
from openai import OpenAI
import psycopg
import json
import os
from datetime import datetime

app = Flask(__name__)

EXPECTED_API_KEY = os.environ.get("LEAD_API_KEY")
DATABASE_URL = os.environ.get("DATABASE_URL", "dbname=lead_db")


def classify_lead(service, message):
    client = OpenAI()

    response = client.responses.create(
        model="gpt-5-mini",
        instructions=(
            "You classify business sales leads. "
            "Return only valid JSON with exactly these fields: "
            "summary, service_category, urgency, next_action. "
            "Urgency must be exactly Low, Medium, or High. "
            "Do not add extra text."
        ),
        input=f"Service requested: {service}\nCustomer message: {message}"
    )

    result = json.loads(response.output_text)

    required_fields = [
        "summary",
        "service_category",
        "urgency",
        "next_action"
    ]

    for field in required_fields:
        if field not in result:
            raise ValueError(f"Missing AI field: {field}")

    if result["urgency"] not in ["Low", "Medium", "High"]:
        raise ValueError("AI returned an invalid urgency")

    return result


def lead_already_exists(lead_id):
    with psycopg.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT 1 FROM sales_leads WHERE lead_id = %s",
                (lead_id,)
            )
            return cursor.fetchone() is not None


def save_lead(record):
    with psycopg.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO sales_leads (
                    lead_id,
                    customer_name,
                    customer_email,
                    service,
                    message,
                    summary,
                    service_category,
                    urgency,
                    next_action,
                    status
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    record["lead_id"],
                    record["customer_name"],
                    record["customer_email"],
                    record["service"],
                    record["message"],
                    record["summary"],
                    record["service_category"],
                    record["urgency"],
                    record["next_action"],
                    record["status"]
                )
            )

            saved_id = cursor.fetchone()[0]
            connection.commit()
            return saved_id


def log_event(event):
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "event": event
    }

    with open("lead_audit.jsonl", "a") as file:
        file.write(json.dumps(log_entry) + "\n")


@app.get("/health")
def health():
    return jsonify({"status": "ok"}), 200


@app.post("/lead")
def receive_lead():
    provided_api_key = request.headers.get("X-API-Key")

    if not EXPECTED_API_KEY or provided_api_key != EXPECTED_API_KEY:
        return jsonify({
            "received": False,
            "error": "Unauthorized"
        }), 401

    lead_data = request.get_json() or {}

    lead_id = lead_data.get("lead_id", "").strip()
    name = lead_data.get("name", "").strip()
    email = lead_data.get("email", "").strip().lower()
    service = lead_data.get("service", "").strip()
    message = lead_data.get("message", "").strip()

    if not lead_id or not name or not email or not service or not message:
        result = {
            "received": False,
            "status": "invalid",
            "error": "lead_id, name, email, service, and message are required"
        }
        log_event(result)
        return jsonify(result), 200

    if lead_already_exists(lead_id):
        result = {
            "received": False,
            "duplicate": True,
            "message": "This lead was already processed",
            "lead_id": lead_id
        }
        log_event(result)
        return jsonify(result), 200

    try:
        ai_result = classify_lead(service, message)
    except Exception:
        result = {
            "received": False,
            "status": "human_review",
            "error": "AI lead classification failed",
            "lead_id": lead_id
        }
        log_event(result)
        return jsonify(result), 422

    record = {
        "lead_id": lead_id,
        "customer_name": name,
        "customer_email": email,
        "service": service,
        "message": message,
        "summary": ai_result["summary"],
        "service_category": ai_result["service_category"],
        "urgency": ai_result["urgency"],
        "next_action": ai_result["next_action"],
        "status": "classified"
    }

    database_id = save_lead(record)

    result = {
        "received": True,
        "saved": True,
        "database_id": database_id,
        "lead": record
    }

    log_event(result)
    return jsonify(result), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5060, debug=True)
