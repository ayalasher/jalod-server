import importlib
import os
from datetime import datetime

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


def test_member_crud_flow(client):
    import src.app as app_module
    from src.models.member import memberModel

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

    list_response = client.get("/members")
    assert list_response.status_code == 200
    members = list_response.get_json()
    assert len(members) == 1

    get_response = client.get(f"/members/{created_member['id']}")
    assert get_response.status_code == 200
    fetched_member = get_response.get_json()
    assert fetched_member["name"] == "Grace"

    update_payload = {"name": "Grace Hopper"}
    update_response = client.put(f"/members/{created_member['id']}", json=update_payload)
    assert update_response.status_code == 200
    updated_member = update_response.get_json()
    assert updated_member["name"] == "Grace Hopper"

    delete_response = client.delete(f"/members/{created_member['id']}")
    assert delete_response.status_code == 204

    with app_module.app.app_context():
        assert memberModel.query.get(created_member["id"]) is None
