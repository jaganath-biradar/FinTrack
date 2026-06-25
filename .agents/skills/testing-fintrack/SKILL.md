---
name: testing-fintrack
description: Run and test the FinTrack FastAPI personal-finance app locally end-to-end. Use when verifying UI/API changes to expenses, income, budgets, auth, or other pages.
---

# Testing FinTrack locally

FinTrack is a FastAPI + SQLAlchemy + SQLite app with Jinja2 server-rendered templates and a cookie-based JWT auth. The DB auto-creates on startup via `Base.metadata.create_all`, so no migrations are needed to run.

## Setup gotchas (requirements.txt is broken)
`pip install -r requirements.txt` fails — several pins don't exist on PyPI and one dep is missing. Install working versions instead:

```bash
python3 -m venv venv && source venv/bin/activate
pip install fastapi==0.115.0 "uvicorn[standard]==0.30.0" sqlalchemy==2.0.20 \
  alembic==1.12.1 jinja2==3.1.4 python-jose==3.4.0 "passlib[bcrypt]==1.7.4" bcrypt==4.0.1 \
  python-multipart==0.0.6 python-dotenv==1.1.1 reportlab==4.0.0 email-validator
```

Key points (these may be fixed in future — check `requirements.txt` first):
- `alembic==1.12.2`, `python-jose==3.4.2`, `passlib==1.7.5` in requirements.txt do not exist on PyPI; use nearby valid versions.
- `email-validator` is missing but required (pydantic `EmailStr` on the user schema).
- `passlib==1.7.4` crashes with `bcrypt>=5` (`ValueError: password cannot be longer than 72 bytes`) during register/login. Pin `bcrypt==4.0.1`. If you see that error on `/auth/register-form` returning a 500, this is the cause.
- `reportlab` pulls `pycairo`, which needs system `pkg-config` + `libcairo2-dev` (`sudo apt-get install -y pkg-config libcairo2-dev`).

## Run
```bash
source venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8000
```
Server log to a file when backgrounding so you can inspect tracebacks (500s render as a bare "Internal Server Error" page).

## Auth flow (no test account persists — DB is fresh each build)
Register a user, then log in:
1. `/register` — fill Full Name, Email, Password → submits to `/auth/register-form`, redirects to `/login?registered=1`.
2. `/login` — Email + Password → sets `access_token` cookie, redirects to `/dashboard`.
Example creds for local testing: `testuser@example.com` / `Password123!`.

## Expenses page testing
- Page: `/expenses`. Form fields: `expense_name`, `category` (select), `amount`, `expense_date` (HTML date input).
- Date input tip: typing into the native date field is finicky; clicking it opens a calendar popup — click the day directly to set it reliably.
- Stat cards: "Transactions" (count), "Total Spent", and the "(N records)" header reflect server state after the page reloads.
- On successful add, the inline script shows a green success message then reloads after ~0.9s.

### Regression: duplicate add/delete
The expense form submit + row-delete handlers must only be bound ONCE. They live in the inline `<script>` in `app/templates/expenses.html`; do NOT re-add them in `app/static/js/app.js` (that caused every add/delete to fire twice). To verify: on a fresh account, add one expense with a single click and confirm Transactions shows `1` (not `2`) and exactly one matching row appears. A doubled count/total means the duplicate-binding bug is back.

## Devin Secrets Needed
None — runs fully locally with a self-created account and SQLite.
