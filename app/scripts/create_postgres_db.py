import os
from urllib.parse import urlparse, urlunparse
from sqlalchemy import create_engine, text
from app.config import load_env

load_env()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not set")

# Connect to the default 'postgres' database to create the target DB
parsed = urlparse(DATABASE_URL)
target_db = parsed.path.lstrip('/') or 'personal_finance'
admin_path = '/postgres'
admin_parsed = parsed._replace(path=admin_path)
admin_url = urlunparse(admin_parsed)

engine = create_engine(admin_url)
with engine.connect() as conn:
    conn = conn.execution_options(isolation_level="AUTOCOMMIT")
    try:
        print(f"Creating database '{target_db}' if it does not exist...")
        conn.execute(text(f"CREATE DATABASE {target_db}"))
        print("Database created")
    except Exception as exc:
        msg = str(exc)
        if 'already exists' in msg or 'duplicate database' in msg.lower():
            print("Database already exists")
        else:
            raise
