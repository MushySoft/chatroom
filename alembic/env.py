from logging.config import fileConfig
from sqlalchemy import create_engine
from sqlalchemy import pool
from alembic import context

from src import settings
from src.database import Base
from src.chat.models import *
from src.auth.models import *

if context.config.config_file_name is not None:
    fileConfig(context.config.config_file_name)

ALEMBIC_DATABASE_URL = settings.ALEMBIC_DATABASE_URL
engine = create_engine(ALEMBIC_DATABASE_URL, poolclass=pool.NullPool)

target_metadata = Base.metadata

def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine.connect()
    with connectable as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True
        )

        with context.begin_transaction():
            context.run_migrations()

run_migrations_online()
