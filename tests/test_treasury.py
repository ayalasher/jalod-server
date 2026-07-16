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
