      # FinTrack — Personal Finance Management System

      > A fintech-style personal finance dashboard built with **FastAPI**, **SQLAlchemy**, **SQLite**, **Alembic**, **Jinja2**, and **Chart.js**.

      ---

      ## Tech Stack

      | Layer | Technology |
      |---|---|
      | Backend | FastAPI, SQLAlchemy, Alembic |
      | Database | SQLite |
      | Auth | JWT (cookie-based) via python-jose |
      | Templating | Jinja2 |
      | Charts | Chart.js |
      | PDF Reports | ReportLab |
      | UI | Custom dark fintech CSS + Lucide Icons |

      ---

      ## Features

      - User registration and JWT authentication (cookie-based)
      - Income, expense, budget, investment, and savings goal management
      - Dashboard with KPI cards and animated counters
      - Income vs Expenses bar chart + Savings trend line (Chart.js)
      - Expense breakdown doughnut chart by category
      - Budget progress tracking with overspend alerts
      - PDF monthly financial report generation
      - All values displayed in Indian Rupees (₹)
      - Responsive dark fintech UI

      ---

      ## Setup

      ### 1. Clone the repository

      ```bash
      git clone https://github.com/your-username/fintrack.git  # replace with your actual URL
      cd fintrack
      ```

      ### 2. Create and activate a virtual environment

      ```bash
      python -m venv venv

      # Windows
      venv\Scripts\activate

      # macOS / Linux
      source venv/bin/activate
      ```

      ### 3. Install dependencies

      ```bash
      pip install -r requirements.txt
      ```

      ### 4. Configure environment variables

      ```bash
      cp .env.example .env
      ```

      Open `.env` and update `SECRET_KEY` with a secure random string.

      ### 5. Run database migrations

      ```bash
      alembic upgrade head
      ```

      ### 6. Start the app

      ```bash
      uvicorn app.main:app --reload
      ```

      ### 7. Open in browser

      Visit [http://127.0.0.1:80001](http://127.0.0.1:80001)

      ---

      ## Usage

      - Go to `/register` to create a new account
      - Go to `/login` to sign in
      - Unauthenticated users are automatically redirected to `/login`
      - Use `/reports` to download a monthly PDF financial summary

      ---

      ## Project Structure

      ```
      fintrack/
      ├── app/
      │   ├── auth/          # JWT utilities
      │   ├── models/        # SQLAlchemy models
      │   ├── routers/       # FastAPI route handlers
      │   ├── schemas/       # Pydantic schemas
      │   ├── static/        # CSS and JS
      │   ├── templates/     # Jinja2 HTML templates
      │   ├── utils/         # PDF report generation
      │   ├── config.py
      │   ├── database.py
      │   └── main.py
      ├── alembic/           # Database migrations
      ├── .env.example
      ├── requirements.txt
      └── README.md
      ```

      ---

      ## Notes

      - The app uses **SQLite** by default — no external database setup required.
      - The `personal_finance.db` file is excluded from version control via `.gitignore`.
      - To reset the database, delete `personal_finance.db` and re-run `alembic upgrade head`.

      ---

      ## License

      This project is open source and available under the [MIT License](LICENSE).
