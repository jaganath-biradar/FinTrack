import sys
print("Creating database tables...")
try:
    from app.database import engine, Base
    # Import all models so Base.metadata knows about every table
    from app.models import User, Income, Expense, Budget, Investment, SavingsGoal  # noqa: F401
    Base.metadata.create_all(bind=engine)
    print(f"Tables created successfully on: {engine.url}")
except Exception as e:
    print(f"Table creation failed: {e}", file=sys.stderr)
    sys.exit(1)
