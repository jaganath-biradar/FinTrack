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

print("Running alembic upgrade head...")
result = subprocess.run(["alembic", "upgrade", "head"], capture_output=False)
if result.returncode != 0:
    print("FAILED: alembic upgrade head", file=sys.stderr)
    sys.exit(1)

print("=" * 60)
print("PRESTART: Done")
print("=" * 60)
