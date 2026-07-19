import importlib
import os
from datetime import datetime

import pytest


def test_member_crud_flow(client):
    import src.app as app_module
    from src.models.member import memberModel

    auth_payload = {
        "name": "AuthUser",
        "email_address": "authuser@example.com",
        "phone_number": 111222333,
        "password": "password123",
    }

    auth_response = client.post("/auth/signup", json=auth_payload)
    assert auth_response.status_code == 201
    token = auth_response.get_json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    create_payload = {
        "name": "Grace",
        "email_address": "grace@example.com",
        "phone_number": 123456789,
        "birthday": "1990-04-03T00:00:00",
    }

    create_response = client.post("/members", json=create_payload)
    assert create_response.status_code == 201
    created_member = create_response.get_json()
    assert created_member["name"] == "Grace"
    assert created_member["email_address"] == "grace@example.com"

    list_response = client.get("/members", headers=headers)
    assert list_response.status_code == 200
    members = list_response.get_json()
    assert len(members) == 2
    assert any(member["name"] == "Grace" for member in members)

    get_response = client.get(f"/members/{created_member['id']}")
    assert get_response.status_code == 200
    fetched_member = get_response.get_json()
    assert fetched_member["name"] == "Grace"

    update_payload = {"name": "Grace Hopper"}
    update_response = client.put(f"/members/{created_member['id']}", json=update_payload)
    assert update_response.status_code == 200
    updated_member = update_response.get_json()
    assert updated_member["name"] == "Grace Hopper"

    delete_response = client.delete(f"/members/{created_member['id']}", headers=headers)
    assert delete_response.status_code == 204

    from src.db import db as _db

    with app_module.app.app_context():
        # Use Session.get() to avoid SQLAlchemy legacy Query.get() in tests.
        assert _db.session.get(memberModel, created_member["id"]) is None


def test_member_default_role_is_user(client):
    import src.app as app_module
    from src.models.member import memberModel

    signup_payload = {
        "name": "Alex",
        "email_address": "alex@example.com",
        "phone_number": 987654321,
        "password": "password123",
    }

    signup_response = client.post("/auth/signup", json=signup_payload)
    assert signup_response.status_code == 201
    created_member = signup_response.get_json()["member"]
    assert created_member["role"] == memberModel.USER_ROLE

    from src.db import db as _db

    with app_module.app.app_context():
        member = _db.session.get(memberModel, created_member["id"])
        assert member is not None
        assert member.role == memberModel.USER_ROLE
        assert not member.is_admin()


def test_members_require_authentication_for_list_and_delete(client):
    response = client.get("/members")
    assert response.status_code == 401

    response = client.delete("/members/1")
    assert response.status_code == 401


def test_member_create_get_update_public(client):
    create_response = client.post(
        "/members",
        json={"name": "Test", "email_address": "test@example.com", "phone_number": 555000111, "birthday": "1990-01-01T00:00:00"},
    )
    assert create_response.status_code == 201
    created_member = create_response.get_json()

    get_response = client.get(f"/members/{created_member['id']}")
    assert get_response.status_code == 200

    update_response = client.put(
        f"/members/{created_member['id']}",
        json={"name": "Test2"},
    )
    assert update_response.status_code == 200
    assert update_response.get_json()["name"] == "Test2"
