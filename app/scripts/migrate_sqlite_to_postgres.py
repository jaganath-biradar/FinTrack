"""Migrate data from local SQLite (personal_finance.db) to PostgreSQL.

Usage: set `DATABASE_URL` env to the Postgres DB, then run:
    python -m app.scripts.migrate_sqlite_to_postgres

This script reads rows from the SQLite DB and inserts them into Postgres.
It creates tables in Postgres from `Base.metadata` if they don't exist.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import load_env

load_env()

SQLITE_URL = os.getenv("SQLITE_URL", "sqlite:///./personal_finance.db")
PG_URL = os.getenv("DATABASE_URL")

if not PG_URL:
    raise RuntimeError("Set DATABASE_URL environment variable to target Postgres DB")

# Import models (they use the shared Base)
from app.database import Base
from app.models.user import User
from app.models.income import Income
from app.models.expense import Expense
from app.models.budget import Budget
from app.models.investment import Investment
from app.models.savings_goal import SavingsGoal

# Create engines & sessions
src_engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
dst_engine = create_engine(PG_URL)

SrcSession = sessionmaker(bind=src_engine)
DstSession = sessionmaker(bind=dst_engine)


def copy_table(src_session, dst_session, model, preserve_pk=True):
    rows = src_session.query(model).all()
    print(f"Copying {len(rows)} rows for {model.__name__}")
    for row in rows:
        data = {c.name: getattr(row, c.name) for c in row.__table__.columns}
        if not preserve_pk:
            data.pop("id", None)
        obj = model(**data)
        dst_session.add(obj)
    dst_session.commit()


def main():
    # Ensure destination tables exist
    Base.metadata.create_all(bind=dst_engine)

    src = SrcSession()
    dst = DstSession()
    try:
        # Copy in order respecting FKs: users first
        copy_table(src, dst, User, preserve_pk=True)
        copy_table(src, dst, Income, preserve_pk=True)
        copy_table(src, dst, Expense, preserve_pk=True)
        copy_table(src, dst, Budget, preserve_pk=True)
        copy_table(src, dst, Investment, preserve_pk=True)
        copy_table(src, dst, SavingsGoal, preserve_pk=True)
        print("Data copy complete")
    finally:
        src.close()
        dst.close()


if __name__ == "__main__":
    main()
