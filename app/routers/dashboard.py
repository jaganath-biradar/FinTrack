from datetime import date
from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, extract
from sqlalchemy.orm import Session
from app.auth.utils import get_current_user
from app.database import get_db
from app.models import Income, Expense, Investment, Budget, SavingsGoal

router = APIRouter(tags=["Dashboard"])
templates = Jinja2Templates(directory="app/templates")


def safe_sum(value):
    return float(value or 0.0)


def recent_months(today: date, count: int = 6):
    months = []
    year = today.year
    month = today.month
    for _ in range(count):
        months.append((year, month, date(year, month, 1).strftime("%b")))
        month -= 1
        if month == 0:
            month = 12
            year -= 1
    return list(reversed(months))


@router.get("/dashboard")
def dashboard(request: Request, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    today = date.today()
    current_month = today.month
    current_year = today.year
    chart_months = recent_months(today)

    total_income = safe_sum(
        db.query(func.sum(Income.amount)).filter(Income.user_id == current_user.id).scalar()
    )
    total_expenses = safe_sum(
        db.query(func.sum(Expense.amount)).filter(Expense.user_id == current_user.id).scalar()
    )
    total_investments = safe_sum(
        db.query(func.sum(Investment.amount)).filter(Investment.user_id == current_user.id).scalar()
    )
    total_savings = max(total_income - total_expenses, 0.0)
    net_worth = total_income - total_expenses + total_investments
    savings_rate = round((total_savings / total_income * 100), 1) if total_income else 0.0

    expense_categories = ["Food", "Rent", "Travel", "Shopping", "Healthcare", "Utilities", "Entertainment", "Education", "Others"]
    expense_breakdown = [
        safe_sum(
            db.query(func.sum(Expense.amount))
            .filter(Expense.user_id == current_user.id)
            .filter(Expense.category == category)
            .scalar()
        )
        for category in expense_categories
    ]

    income_vs_expense = [
        safe_sum(
            db.query(func.sum(Income.amount))
            .filter(Income.user_id == current_user.id)
            .filter(extract("month", Income.income_date) == month)
            .filter(extract("year", Income.income_date) == year)
            .scalar()
        )
        for year, month, _ in chart_months
    ]
    expense_trend = [
        safe_sum(
            db.query(func.sum(Expense.amount))
            .filter(Expense.user_id == current_user.id)
            .filter(extract("month", Expense.expense_date) == month)
            .filter(extract("year", Expense.expense_date) == year)
            .scalar()
        )
        for year, month, _ in chart_months
    ]

    investment_labels = ["Stocks", "Mutual Funds", "SIP", "PPF", "NPS", "Fixed Deposit", "Gold", "Crypto"]
    investment_breakdown = [
        safe_sum(
            db.query(func.sum(Investment.amount))
            .filter(Investment.user_id == current_user.id)
            .filter(Investment.investment_type == label)
            .scalar()
        )
        for label in investment_labels
    ]

    budgets = (
        db.query(Budget)
        .filter(Budget.user_id == current_user.id, Budget.month == current_month, Budget.year == current_year)
        .order_by(Budget.category)
        .all()
    )
    budget_status = []
    for budget in budgets:
        spent_amount = safe_sum(
            db.query(func.sum(Expense.amount))
            .filter(Expense.user_id == current_user.id)
            .filter(Expense.category == budget.category)
            .filter(extract("month", Expense.expense_date) == current_month)
            .filter(extract("year", Expense.expense_date) == current_year)
            .scalar()
        )
        used_percent = round((spent_amount / float(budget.monthly_limit) * 100), 1) if budget.monthly_limit else 0.0
        budget_status.append(
            {
                "category": budget.category,
                "limit": f"₹{budget.monthly_limit:,.2f}",
                "spent": f"₹{spent_amount:,.2f}",
                "remaining": f"₹{max(budget.monthly_limit - spent_amount, 0.0):,.2f}",
                "percent": used_percent,
                "status": "danger" if used_percent > 100 else "warning" if used_percent >= 80 else "success",
            }
        )

    recent_incomes = (
        db.query(Income)
        .filter(Income.user_id == current_user.id)
        .order_by(Income.income_date.desc())
        .limit(5)
        .all()
    )
    recent_expenses = (
        db.query(Expense)
        .filter(Expense.user_id == current_user.id)
        .order_by(Expense.expense_date.desc())
        .limit(5)
        .all()
    )

    goals = (
        db.query(SavingsGoal)
        .filter(SavingsGoal.user_id == current_user.id)
        .order_by(SavingsGoal.target_date)
        .limit(4)
        .all()
    )

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "page_title": "Dashboard",
            "current_user": current_user,
            "today": today.strftime("%B %Y"),
            "kpis": {
                "total_income": f"₹{total_income:,.2f}",
                "total_expenses": f"₹{total_expenses:,.2f}",
                "total_savings": f"₹{total_savings:,.2f}",
                "total_investments": f"₹{total_investments:,.2f}",
                "net_worth": f"₹{net_worth:,.2f}",
                "savings_rate": f"{savings_rate}%",
            },
            "expense_labels": expense_categories,
            "expense_values": expense_breakdown,
            "chart_labels": [label for _, _, label in chart_months],
            "income_values": income_vs_expense,
            "expense_values_monthly": expense_trend,
            "investment_labels": investment_labels,
            "investment_values": investment_breakdown,
            "budget_status": budget_status,
            "recent_incomes": recent_incomes,
            "recent_expenses": recent_expenses,
            "goals": goals,
        },
    )
