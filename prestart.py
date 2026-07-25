import sys
import os
import subprocess

print("=" * 60)
print("PRESTART: Beginning database initialization")
print("=" * 60)

raw_url = os.getenv("DATABASE_URL", "NOT SET")
if "://" in raw_url:
    scheme = raw_url.split("://")[0]
    rest = raw_url.split("@")[-1] if "@" in raw_url else raw_url.split("://")[1]
    print(f"DATABASE_URL scheme: {scheme}")
    print(f"DATABASE_URL host/db: {rest}")
else:
    print(f"DATABASE_URL: {raw_url}")

if raw_url.startswith("postgres://"):
    os.environ["DATABASE_URL"] = raw_url.replace("postgres://", "postgresql://", 1)
    print("Fixed postgres:// -> postgresql://")

# If alembic_version table exists but is empty (tables created outside Alembic),
# stamp as 0001_initial so Alembic skips straight to running 0002+
try:
    import sqlalchemy as sa
    db_url = os.environ.get("DATABASE_URL", raw_url)
    engine = sa.create_engine(db_url)
    with engine.connect() as conn:
        inspector = sa.inspect(engine)
        tables = inspector.get_table_names()
        print(f"Existing tables: {tables}")

        has_version_table = "alembic_version" in tables
        has_users = "users" in tables

        if has_users and not has_version_table:
            # Tables exist but Alembic has never been run — stamp as base revision
            print("Tables exist with no alembic_version — stamping as 0001_initial...")
            result = subprocess.run(["alembic", "stamp", "0001_initial"], capture_output=False)
            if result.returncode != 0:
                print("FAILED: alembic stamp", file=sys.stderr)
                sys.exit(1)
        elif has_version_table:
            row = conn.execute(sa.text("SELECT version_num FROM alembic_version")).fetchone()
            print(f"Current alembic version: {row[0] if row else 'empty'}")
            if not row:
                print("alembic_version table is empty — stamping as 0001_initial...")
                result = subprocess.run(["alembic", "stamp", "0001_initial"], capture_output=False)
                if result.returncode != 0:
                    print("FAILED: alembic stamp", file=sys.stderr)
                    sys.exit(1)
except Exception as e:
    print(f"WARNING: pre-check failed ({e}) — proceeding with upgrade anyway")

print("Running alembic upgrade head...")
result = subprocess.run(["alembic", "upgrade", "head"], capture_output=False)
if result.returncode != 0:
    print("FAILED: alembic upgrade head", file=sys.stderr)
    sys.exit(1)

print("=" * 60)
print("PRESTART: Done")
print("=" * 60)
