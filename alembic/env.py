"""Alembic environment.

Doc: https://alembic.sqlalchemy.org/en/latest/tutorial.html
"""

from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# --- App glue: load .env + expose Base.metadata for autogenerate ---
from app.core.config import get_settings  # noqa: E402
from app.db.base import Base  # noqa: E402

# Import models so they register on Base.metadata before autogenerate scans.
# (Safe to import even if files don't exist yet — we'll create app.db.base below.)
import app.models  # noqa: E402, F401  # noqa

# Alembic Config object (reads alembic.ini)
config = context.config

# Inject DATABASE_URL from our settings (overrides sqlalchemy.url from ini)
config.set_main_option("sqlalchemy.url", get_settings().sqlalchemy_database_uri)

# Configure Python logging from ini file
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata target for 'alembic revision --autogenerate'
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Emit SQL statements to stdout — no DB connection required."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations against a live DB connection."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()