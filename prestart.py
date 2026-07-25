import sys
import os

print("=" * 60)
print("PRESTART: Beginning database initialization")
print("=" * 60)

# Step 1: Show raw DATABASE_URL (masked password)
raw_url = os.getenv("DATABASE_URL", "NOT SET")
if "://" in raw_url:
    scheme = raw_url.split("://")[0]
    rest = raw_url.split("@")[-1] if "@" in raw_url else raw_url.split("://")[1]
    print(f"DATABASE_URL scheme: {scheme}")
    print(f"DATABASE_URL host/db: {rest}")
else:
    print(f"DATABASE_URL: {raw_url}")

# Step 2: Fix postgres:// -> postgresql://
DATABASE_URL = raw_url
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    print("Fixed postgres:// -> postgresql://")

print(f"Is SQLite: {DATABASE_URL.startswith('sqlite')}")

# Step 3: Import Base and models
try:
    from app.database import Base, engine
    print(f"Engine URL: {engine.url}")
except Exception as e:
    print(f"FAILED to import database: {e}", file=sys.stderr)
    sys.exit(1)

try:
    from app.models.user import User
    from app.models.income import Income
    from app.models.expense import Expense
    from app.models.budget import Budget
    from app.models.investment import Investment
    from app.models.savings_goal import SavingsGoal
    print("All models imported successfully")
except Exception as e:
    print(f"FAILED to import models: {e}", file=sys.stderr)
    sys.exit(1)

# Step 4: Show what Base.metadata sees
tables = list(Base.metadata.tables.keys())
print(f"Tables in Base.metadata: {tables}")

if not tables:
    print("ERROR: Base.metadata has NO tables — models not registered!", file=sys.stderr)
    sys.exit(1)

# Step 5: Run create_all
try:
    print("Running Base.metadata.create_all()...")
    Base.metadata.create_all(bind=engine)
    print("SUCCESS: All tables created/verified")
except Exception as e:
    print(f"FAILED create_all: {e}", file=sys.stderr)
    sys.exit(1)

print("=" * 60)
print("PRESTART: Done")
print("=" * 60)
