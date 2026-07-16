import importlib
import os

import pytest


@pytest.fixture()
def client(tmp_path):
    db_path = tmp_path / "test.db"
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"

    import src.app as app_module

    importlib.reload(app_module)
    app_module.app.config.update(TESTING=True)

    with app_module.app.app_context():
        app_module.db.drop_all()
        app_module.db.create_all()
        yield app_module.app.test_client()
        app_module.db.session.remove()
        app_module.db.drop_all()


def test_welfare_list_and_create(client):
    auth_payload = {
        "name": "WelfareUser",
        "email_address": "welfareuser@example.com",
        "phone_number": 555666777,
        "password": "password123",
    }

    auth_response = client.post("/auth/signup", json=auth_payload)
    assert auth_response.status_code == 201
    token = auth_response.get_json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "event_id": 1,
        "event_name": "Community Support",
        "date": "2026-01-15T00:00:00",
        "description": "Food distribution",
        "amount_spent": 2500.00,
        "status": "Done",
    }

    create_response = client.post("/welfare", json=payload, headers=headers)
    assert create_response.status_code == 201
    created = create_response.get_json()
    assert created["event_name"] == "Community Support"
    assert created["status"] == "Done"

    list_response = client.get("/welfare")
    assert list_response.status_code == 200
    welfare_items = list_response.get_json()
    assert len(welfare_items) == 1
    assert welfare_items[0]["event_name"] == "Community Support"

    get_response = client.get(f"/welfare/{created['id']}")
    assert get_response.status_code == 200
    single_item = get_response.get_json()
    assert single_item["event_name"] == "Community Support"
