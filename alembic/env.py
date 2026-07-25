import os
import sys
from logging.config import fileConfig
from sqlalchemy import create_engine, pool
from alembic import context
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import Base
from app.models import User, Income, Expense, Budget, Investment, SavingsGoal  # noqa: F401

config = context.config
fileConfig(config.config_file_name)

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./personal_finance.db")
config.set_main_option("sqlalchemy.url", DATABASE_URL)


def run_migrations_offline():
    context.configure(
        url=DATABASE_URL,
        target_metadata=Base.metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = create_engine(DATABASE_URL, poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=Base.metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
