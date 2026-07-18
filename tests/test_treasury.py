import importlib
import os

import pytest


def test_treasury_get_requires_authentication(client):
    response = client.get("/treasury")

    assert response.status_code == 401


def test_treasury_get_requires_admin_role(client):
    import src.app as app_module
    from src.models.member import memberModel

    signup_payload = {
        "name": "User",
        "email_address": "user@example.com",
        "phone_number": 111222333,
        "password": "password123",
    }

    signup_response = client.post("/auth/signup", json=signup_payload)
    assert signup_response.status_code == 201
    token = signup_response.get_json()["access_token"]

    response = client.get("/treasury", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403

    with app_module.app.app_context():
        member = memberModel.query.filter_by(name="User").first()
        assert member is not None
        member.role = memberModel.ADMIN_ROLE
        app_module.db.session.commit()

    login_payload = {
        "name": "User",
        "password": "password123",
    }
    login_response = client.post("/auth/login", json=login_payload)
    assert login_response.status_code == 200
    admin_token = login_response.get_json()["access_token"]

    admin_response = client.get("/treasury", headers={"Authorization": f"Bearer {admin_token}"})
    assert admin_response.status_code == 200
    assert admin_response.get_json() == []
