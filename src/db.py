import os
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from sqlalchemy import inspect, text
from sqlalchemy.pool import NullPool
from flask_sqlalchemy import SQLAlchemy


# Central SQLAlchemy instance used across the application.
# Import and call `configure_database(app)` from `src.app` to attach
# the SQLAlchemy `db` object to the Flask application instance.
db = SQLAlchemy()


def _normalize_database_url(database_url: str) -> str:
    """Convert common Neon/Postgres URLs into a SQLAlchemy-compatible URI.

    Some managed Postgres providers expose URIs that are not directly compatible
    with SQLAlchemy. This helper normalizes common variants and ensures
    recommended query params (e.g. `sslmode=require`).
    """

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

    # Read database URL from environment (support multiple names).
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
    # Choose sane engine options depending on the database type. For SQLite
    # (used in tests), prefer NullPool so connections are not retained in a
    # pool and are closed immediately when no longer needed. For other DBs
    # (e.g., Postgres) use a reused pool with pre-ping enabled for resilience.
    if database_url.startswith("sqlite:"):
        app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
            "poolclass": NullPool,
        }
    else:
        app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
            "pool_size": 10,
            "pool_recycle": 3600,
            "pool_pre_ping": True,
        }

    db.init_app(app)

    return db


def ensure_member_auth_columns(app):
    """Add auth columns to an existing Members table when the database was created before auth support.

    This helper is intentionally conservative: it only adds missing columns
    rather than attempting destructive schema changes. It is run on app
    startup to incrementally migrate older databases to the fields required
    by the authentication and contributions features.
    """

    with app.app_context():
        inspector = inspect(db.engine)

        # If the Members table does not exist yet, nothing to migrate.
        if "Members" not in inspector.get_table_names():
            return

        existing_columns = {column["name"] for column in inspector.get_columns("Members")}

        with db.engine.begin() as connection:
            # Add a password_hash column for storing hashed passwords.
            if "password_hash" not in existing_columns:
                connection.execute(text('ALTER TABLE "Members" ADD COLUMN password_hash VARCHAR(255)'))

            # Contribution-related columns used by business logic.
            if "contributions_tier" not in existing_columns:
                connection.execute(text('ALTER TABLE "Members" ADD COLUMN contributions_tier NUMERIC(10, 2)'))

            if "contributions_debt" not in existing_columns:
                connection.execute(text('ALTER TABLE "Members" ADD COLUMN contributions_debt NUMERIC(10, 2)'))

            if "loans_debt" not in existing_columns:
                connection.execute(text('ALTER TABLE "Members" ADD COLUMN loans_debt NUMERIC(10, 2)'))

            if "contributions_dated_at" not in existing_columns:
                connection.execute(text('ALTER TABLE "Members" ADD COLUMN contributions_dated_at TIMESTAMP'))

            # Add a simple role column with a safe default. This supports lightweight
            # role checks without a full RBAC system.
            if "role" not in existing_columns:
                connection.execute(text('ALTER TABLE "Members" ADD COLUMN role VARCHAR(10) NOT NULL DEFAULT \'user\''))

            # PostgreSQL-specific adjustments to ensure non-null constraints and
            # sensible defaults for upgraded tables.
            if db.engine.dialect.name == "postgresql" and "password_hash" not in existing_columns:
                connection.execute(text('UPDATE "Members" SET password_hash = \'\' WHERE password_hash IS NULL'))
                connection.execute(text('ALTER TABLE "Members" ALTER COLUMN password_hash SET DEFAULT \'\''))
                connection.execute(text('ALTER TABLE "Members" ALTER COLUMN password_hash SET NOT NULL'))

            if db.engine.dialect.name == "postgresql":
                # Make `age_group` nullable on PostgreSQL to match application expectations.
                connection.execute(text('ALTER TABLE "Members" ALTER COLUMN age_group DROP NOT NULL'))
                connection.execute(text('ALTER TABLE "Members" ALTER COLUMN age_group DROP NOT NULL'))