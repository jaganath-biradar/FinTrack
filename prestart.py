import sys
import os
import sqlalchemy as sa

print("=" * 60)
print("PRESTART: Beginning database initialization")
print("=" * 60)

raw_url = os.getenv("DATABASE_URL", "NOT SET")
if raw_url.startswith("postgres://"):
    raw_url = raw_url.replace("postgres://", "postgresql://", 1)
    os.environ["DATABASE_URL"] = raw_url
    print("Fixed postgres:// -> postgresql://")

print(f"Connecting to DB...")

try:
    engine = sa.create_engine(raw_url)
    with engine.connect() as conn:

        # 1. Create all tables if they don't exist
        from app.database import Base
        from app.models.user import User
        from app.models.income import Income
        from app.models.expense import Expense
        from app.models.budget import Budget
        from app.models.investment import Investment
        from app.models.savings_goal import SavingsGoal

        Base.metadata.create_all(bind=engine)
        print("create_all() done")

        # 2. Add missing columns to users table (idempotent)
        missing = [
            ("is_verified",         "BOOLEAN NOT NULL DEFAULT FALSE"),
            ("verification_token",  "VARCHAR(128)"),
            ("reset_token",         "VARCHAR(128)"),
            ("reset_token_expires", "TIMESTAMP"),
        ]
        inspector = sa.inspect(engine)
        existing = {c["name"] for c in inspector.get_columns("users")}
        print(f"Existing users columns: {existing}")

        for col, col_type in missing:
            if col not in existing:
                conn.execute(sa.text(f"ALTER TABLE users ADD COLUMN {col} {col_type}"))
                conn.commit()
                print(f"  -> Added column: {col}")
            else:
                print(f"  -> {col} already exists")

except Exception as e:
    print(f"FAILED: {e}", file=sys.stderr)
    sys.exit(1)

print("=" * 60)
print("PRESTART: Done")
print("=" * 60)
