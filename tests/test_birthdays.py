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


def test_fetch_all_birthdays(client):
    import src.app as app_module
    from src.models.member import memberModel

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

    response = client.get("/members/birthdays")

    assert response.status_code == 200
    payload = response.get_json()
    assert len(payload) == 1
    assert payload[0]["name"] == "Ada"
    assert payload[0]["birthday"].startswith("1990-04-03")
