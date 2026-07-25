import sys
import os

print("=" * 60)
print("PRESTART: Starting")
print("=" * 60)

raw_url = os.getenv("DATABASE_URL", "")
if not raw_url:
    print("ERROR: DATABASE_URL is not set", file=sys.stderr)
    sys.exit(1)

if raw_url.startswith("postgres://"):
    raw_url = raw_url.replace("postgres://", "postgresql://", 1)
    os.environ["DATABASE_URL"] = raw_url
    print("Fixed postgres:// -> postgresql://")

import sqlalchemy as sa

try:
    engine = sa.create_engine(raw_url)
    with engine.connect() as conn:

        # Add all 4 columns using IF NOT EXISTS — fully idempotent
        statements = [
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS is_verified BOOLEAN NOT NULL DEFAULT FALSE",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS verification_token VARCHAR(128)",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS reset_token VARCHAR(128)",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS reset_token_expires TIMESTAMP",
        ]
        for sql in statements:
            print(f"Executing: {sql}")
            conn.execute(sa.text(sql))
            conn.commit()
            print("  -> OK")

        # Verify all columns now exist
        result = conn.execute(sa.text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = 'users' ORDER BY ordinal_position"
        ))
        cols = [r[0] for r in result]
        print(f"users columns after migration: {cols}")

        required = {"is_verified", "verification_token", "reset_token", "reset_token_expires"}
        missing = required - set(cols)
        if missing:
            print(f"ERROR: columns still missing after ALTER: {missing}", file=sys.stderr)
            sys.exit(1)

        print("All required columns verified present.")

except Exception as e:
    print(f"FAILED: {e}", file=sys.stderr)
    sys.exit(1)

print("=" * 60)
print("PRESTART: Done")
print("=" * 60)
