import os
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from sqlalchemy import inspect, text
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


def _normalize_database_url(database_url: str) -> str:
    """Convert common Neon/Postgres URLs into a SQLAlchemy-compatible URI."""

    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql+psycopg2://", 1)
    elif database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+psycopg2://", 1)

    parsed_url = urlparse(database_url)
    query_params = dict(parse_qsl(parsed_url.query, keep_blank_values=True))
    query_params.setdefault("sslmode", "require")
    query_params.pop("channelbinding", None)
    query_params.pop("channel_binding", None)

    return urlunparse(parsed_url._replace(query=urlencode(query_params)))


def configure_database(app):
    """Configure database connection for Flask app."""

    database_url = (
        os.environ.get("DATABASE_URL")
        or os.environ.get("NEON_DATABASE_URL")
        or os.environ.get("POSTGRES_URL")
    )

    if not database_url:
        database_url = "sqlite:///jalod.db"
        print("DATABASE_URL not set, using SQLite as fallback")
    elif database_url.startswith(("postgres://", "postgresql://")):
        database_url = _normalize_database_url(database_url)

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_size": 10,
        "pool_recycle": 3600,
        "pool_pre_ping": True,
    }

    db.init_app(app)

    return db


def ensure_member_auth_columns(app):
    """Add auth columns to an existing Members table when the database was created before auth support."""

    with app.app_context():
        inspector = inspect(db.engine)
        if "Members" not in inspector.get_table_names():
            return

        column_names = {column["name"] for column in inspector.get_columns("Members")}
        if "password_hash" in column_names:
            return

        with db.engine.begin() as connection:
            connection.execute(text('ALTER TABLE "Members" ADD COLUMN password_hash VARCHAR(255)'))

            if db.engine.dialect.name == "postgresql":
                connection.execute(text('UPDATE "Members" SET password_hash = \'\' WHERE password_hash IS NULL'))
                connection.execute(text('ALTER TABLE "Members" ALTER COLUMN password_hash SET DEFAULT \'\''))
                connection.execute(text('ALTER TABLE "Members" ALTER COLUMN password_hash SET NOT NULL'))
                connection.execute(text('ALTER TABLE "Members" ALTER COLUMN age_group DROP NOT NULL'))