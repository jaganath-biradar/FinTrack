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

try:
    from app.database import Base, engine
    from app.models.user import User
    from app.models.income import Income
    from app.models.expense import Expense
    from app.models.budget import Budget
    from app.models.investment import Investment
    from app.models.savings_goal import SavingsGoal
    from app.models.password_reset import PasswordReset

    Base.metadata.create_all(bind=engine)
    print("create_all() done")
except Exception as e:
    print(f"FAILED: {e}", file=sys.stderr)
    sys.exit(1)

print("=" * 60)
print("PRESTART: Done")
print("=" * 60)
