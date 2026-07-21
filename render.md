Deployment to Render
=====================

Quick steps to deploy this FastAPI app to Render and migrate existing SQLite data.

1) Push your code

   ```bash
   git add .
   git commit -m "Prepare for Render deployment: services, Procfile, render.yaml"
   git push origin main
   ```

2) Create a Postgres database on Render

- Dashboard → New → PostgreSQL → create `personal-finance-db` (or use `render.yaml` with the Render CLI).
- Copy the connection URL (Render provides it). You do NOT need to include `postgresql+psycopg://` prefix — Render wiring will set `DATABASE_URL` for you if you reference the database in `render.yaml`.

3) Create a Web Service

- Dashboard → New → Web Service → connect GitHub repo + branch.
- Set Runtime / Environment to `Python 3.12`.
- Set Build Command: `pip install -r requirements.txt`
- Set Start Command: `alembic upgrade head && gunicorn -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:$PORT`
- Add environment variables: `SECRET_KEY` (secure string) and any others you need. If you created the database via Render UI, add the database and Render will expose `DATABASE_URL` automatically.

4) Run migrations

- Migrations will run automatically if you use the Start Command above; otherwise run manually from a shell on Render or locally with `DATABASE_URL` set to the Render DB:

  ```powershell
  $env:DATABASE_URL = '<render_database_url>'
  .venv\Scripts\python.exe -m alembic upgrade head
  ```

5) (Optional) Migrate existing SQLite data to Render Postgres

 - Run the migration script locally pointing at Render DB:

  ```powershell
  $env:DATABASE_URL = '<render_database_url>'
  .venv\Scripts\python.exe -m app.scripts.migrate_sqlite_to_postgres
  ```

6) Verify

- Check Render deploy logs for errors; open the site URL; run a few API calls.
- Confirm the deployed runtime is Python 3.12 in the Render logs.

7) If you still see the same error

- The error usually means the service is still running on Python 3.14.
- In the Render dashboard, open your Web Service settings and verify the runtime is set to `Python 3.12` or `python-3.12.10`.
- If you used a manual service, update the runtime there or recreate the service using `render.yaml`.
- After changing runtime, redeploy the service.

Notes
- `render.yaml` in this repo is a template; fill `branch`, `region`, etc., then use the Render CLI (`render deploy`) or create via dashboard.
- Ensure `requirements.txt` includes `gunicorn` (added) and `psycopg[binary]` so wheels install on Render.
- If you see "unable to infer type for attribute \"name\"" during deploy, this is caused by Render using Python 3.14, not by your app code. Set Render to use Python 3.12.
