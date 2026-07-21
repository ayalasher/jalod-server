import importlib
import os

import pytest


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


def test_welfare_month_combined_response(client):
    # create a member with a birthday in January and another in February
    m1 = {
        "name": "JanMember",
        "email_address": "jan@example.com",
        "phone_number": 111222333,
        "birthday": "1990-01-05T00:00:00",
    }

    m2 = {
        "name": "FebMember",
        "email_address": "feb@example.com",
        "phone_number": 222333444,
        "birthday": "1990-02-10T00:00:00",
    }

    create_m1 = client.post("/members", json=m1)
    assert create_m1.status_code == 201
    create_m2 = client.post("/members", json=m2)
    assert create_m2.status_code == 201

    # sign up an auth user to create a welfare event
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

    # create a welfare event in January 2026
    payload = {
        "event_id": 2,
        "event_name": "January Drive",
        "date": "2026-01-20T00:00:00",
        "description": "Supplies",
        "amount_spent": 100.00,
        "status": "Not Completed",
    }

    create_response = client.post("/welfare", json=payload, headers=headers)
    assert create_response.status_code == 201

    # fetch combined response for January 2026
    resp = client.get("/welfare/month/2026/1")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "events" in data and "birthdays" in data
    assert len(data["events"]) == 1
    # Should include JanMember in birthdays
    assert any(b["name"] == "JanMember" for b in data["birthdays"])
