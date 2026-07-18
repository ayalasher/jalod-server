import importlib
import os
from datetime import datetime

import pytest


def test_fetch_all_birthdays(client):
    import src.app as app_module
    from src.models.member import memberModel

    signup_payload = {
        "name": "AuthUser",
        "email_address": "authuser@example.com",
        "phone_number": 111222333,
        "password": "password123",
    }
    signup_response = client.post("/auth/signup", json=signup_payload)
    assert signup_response.status_code == 201
    token = signup_response.get_json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    with app_module.app.app_context():
        member = memberModel(
            name="Ada",
            email_address="ada@example.com",
            phone_number=123456789,
            birthday=datetime(1990, 4, 3),
            password_hash="hashed",
        )
        app_module.db.session.add(member)
        app_module.db.session.commit()

    response = client.get("/members/birthdays", headers=headers)

    assert response.status_code == 200
    payload = response.get_json()
    assert len(payload) == 1
    assert payload[0]["name"] == "Ada"
    assert payload[0]["birthday"].startswith("1990-04-03")
