import lead_api


def setup_module():
    lead_api.EXPECTED_API_KEY = "lead-demo-key-2026"


def test_missing_api_key_is_rejected():
    client = lead_api.app.test_client()

    response = client.post(
        "/lead",
        json={
            "lead_id": "test-auth-001",
            "name": "Anika",
            "email": "anika@example.com",
            "service": "Bookkeeping",
            "message": "I need help."
        }
    )

    assert response.status_code == 401
    assert response.get_json()["received"] is False


def test_missing_email_is_rejected():
    client = lead_api.app.test_client()

    response = client.post(
        "/lead",
        headers={"X-API-Key": "lead-demo-key-2026"},
        json={
            "lead_id": "test-invalid-001",
            "name": "Anika",
            "service": "Bookkeeping",
            "message": "I need help."
        }
    )

    data = response.get_json()

    assert response.status_code == 200
    assert data["received"] is False
    assert data["status"] == "invalid"


def test_successful_lead_is_classified_and_saved(monkeypatch):
    client = lead_api.app.test_client()

    monkeypatch.setattr(
        lead_api,
        "lead_already_exists",
        lambda lead_id: False
    )

    monkeypatch.setattr(
        lead_api,
        "classify_lead",
        lambda service, message: {
            "summary": "Customer needs bookkeeping help.",
            "service_category": "Bookkeeping",
            "urgency": "Medium",
            "next_action": "Schedule a discovery call"
        }
    )

    monkeypatch.setattr(
        lead_api,
        "save_lead",
        lambda record: 10
    )

    monkeypatch.setattr(
        lead_api,
        "log_event",
        lambda event: None
    )

    response = client.post(
        "/lead",
        headers={"X-API-Key": "lead-demo-key-2026"},
        json={
            "lead_id": "test-success-001",
            "name": "Anika",
            "email": "ANIKA@example.com",
            "service": "Bookkeeping",
            "message": "I need help."
        }
    )

    data = response.get_json()

    assert response.status_code == 200
    assert data["received"] is True
    assert data["saved"] is True
    assert data["database_id"] == 10
    assert data["lead"]["customer_email"] == "anika@example.com"
    assert data["lead"]["urgency"] == "Medium"


def test_duplicate_lead_is_rejected(monkeypatch):
    client = lead_api.app.test_client()

    monkeypatch.setattr(
        lead_api,
        "lead_already_exists",
        lambda lead_id: True
    )

    response = client.post(
        "/lead",
        headers={"X-API-Key": "lead-demo-key-2026"},
        json={
            "lead_id": "test-duplicate-001",
            "name": "Anika",
            "email": "anika@example.com",
            "service": "Bookkeeping",
            "message": "I need help."
        }
    )

    data = response.get_json()

    assert response.status_code == 200
    assert data["received"] is False
    assert data["duplicate"] is True
