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
        test_client = app_module.app.test_client()
        yield test_client
        try:
            test_client.close()
        except Exception:
            pass
        # Ensure all sessions are closed/removed and the engine pool is disposed
        # so that SQLite connections are closed and pytest does not report
        # ResourceWarnings about unclosed databases.
        try:
            app_module.db.session.close()
        except Exception:
            pass
        app_module.db.session.remove()
        app_module.db.drop_all()
        try:
            # Dispose the engine to close any pooled connections.
            app_module.db.engine.dispose()
        except Exception:
            # Be tolerant of environments where engine disposal may fail.
            pass