import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from sqlalchemy import func
from app.models import Income, Expense, Investment, Budget


def create_monthly_report_pdf(user, db, month: int, year: int) -> io.BytesIO:
    buffer = io.BytesIO()
    document = canvas.Canvas(buffer, pagesize=letter)
    document.setTitle(f"Monthly Financial Report - {month}/{year}")

    total_income = float(
        db.query(func.coalesce(func.sum(Income.amount), 0))
        .filter(Income.user_id == user.id)
        .filter(func.extract("month", Income.income_date) == month)
        .filter(func.extract("year", Income.income_date) == year)
        .scalar()
    )
    total_expenses = float(
        db.query(func.coalesce(func.sum(Expense.amount), 0))
        .filter(Expense.user_id == user.id)
        .filter(func.extract("month", Expense.expense_date) == month)
        .filter(func.extract("year", Expense.expense_date) == year)
        .scalar()
    )
    total_investments = float(
        db.query(func.coalesce(func.sum(Investment.amount), 0))
        .filter(Investment.user_id == user.id)
        .filter(func.extract("month", Investment.investment_date) == month)
        .filter(func.extract("year", Investment.investment_date) == year)
        .scalar()
    )

    document.setFont("Helvetica-Bold", 20)
    document.drawString(60, 740, "FinTrack Monthly Financial Report")
    document.setFont("Helvetica", 12)
    document.drawString(60, 720, f"User: {user.full_name}")
    document.drawString(60, 700, f"Month: {month}/{year}")

    document.line(60, 690, 540, 690)
    document.drawString(60, 660, f"Total Income: ₹{total_income:,.2f}")
    document.drawString(60, 640, f"Total Expenses: ₹{total_expenses:,.2f}")
    document.drawString(60, 620, f"Total Investments: ₹{total_investments:,.2f}")
    document.drawString(60, 600, f"Net Savings: ₹{total_income - total_expenses:,.2f}")

    document.setFont("Helvetica-Bold", 14)
    document.drawString(60, 560, "Budget Overview")
    document.setFont("Helvetica", 12)
    budgets = db.query(Budget).filter(Budget.user_id == user.id, Budget.month == month, Budget.year == year).all()
    y = 540
    for budget in budgets:
        document.drawString(70, y, f"{budget.category} - Limit: ₹{budget.monthly_limit:,.2f}")
        y -= 20
    if not budgets:
        document.drawString(70, y, "No budget plans found for this month.")

    document.showPage()
    document.save()
    buffer.seek(0)
    return buffer
