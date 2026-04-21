from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool

from app.core.config import settings
from app.core.database import Base

# Import all models so Alembic can detect them
from app.models import user  # noqa: F401
from app.models import task  # noqa: F401

config = context.config

# Use sync psycopg2 URL for Alembic (strip async driver prefix)
sync_url = settings.database_url.replace("postgresql+asyncpg://", "postgresql://")
config.set_main_option("sqlalchemy.url", sync_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(sync_url, poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
