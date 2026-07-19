## Test database and connection handling

- Tests configure a temporary SQLite database by setting `DATABASE_URL`
  in `tests/conftest.py` (each test run uses a tempfile path).
- To prevent pooled SQLite connections from remaining open after tests
  (which can produce ResourceWarning: unclosed database), the app uses
  `NullPool` for SQLite in `src/db.py` so connections are closed immediately
  instead of being retained in a pool.
- The `client` fixture in `tests/conftest.py` also ensures proper teardown:
  it closes the SQLAlchemy session (`session.close()` and `session.remove()`), and
  calls `engine.dispose()`

Run tests with:

```bash
venv/bin/python -m pytest tests -q
```

If you run into ResourceWarning messages about unclosed databases, make
sure tests are using the `client` fixture from `tests/conftest.py` so the
teardown logic above runs; alternatively prefer running tests with an
in-memory SQLite URL (`sqlite:///:memory:`) or ensure your environment does
not reuse persistent SQLite files between runs.
