from datetime import date
from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, extract
from app.auth.utils import get_current_user
from app.database import get_db
from app.models import Income, Expense, Budget, Investment, SavingsGoal

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def safe_sum(value):
    return float(value or 0.0)


def render_page(request: Request, page_title: str, current_user, template_name: str, **context):
    page_context = {
        "request": request,
        "page_title": page_title,
        "current_user": current_user,
    }
    page_context.update(context)
    return templates.TemplateResponse(template_name, page_context)


@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "page_title": "Login"},
    )


@router.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse(
        "register.html",
        {"request": request, "page_title": "Register"},
    )


@router.get("/income")
def income_page(request: Request, current_user=Depends(get_current_user), db=Depends(get_db)):
    incomes = (
        db.query(Income)
        .filter(Income.user_id == current_user.id)
        .order_by(Income.income_date.desc())
        .all()
    )
    return render_page(
        request,
        "Income",
        current_user,
        "income.html",
        incomes=incomes,
        categories=["Salary", "Freelancing", "Bonus", "Rental Income", "Travel", "Other"],
        today=date.today().strftime("%B %Y"),
    )


@router.get("/expenses")
def expenses_page(request: Request, current_user=Depends(get_current_user), db=Depends(get_db)):
    expenses = (
        db.query(Expense)
        .filter(Expense.user_id == current_user.id)
        .order_by(Expense.expense_date.desc())
        .all()
    )
    return render_page(
        request,
        "Expenses",
        current_user,
        "expenses.html",
        expenses=expenses,
        categories=["Food", "Rent", "Travel", "Shopping", "Healthcare", "Utilities", "Entertainment", "Education", "Others"],
        today=date.today().strftime("%B %Y"),
    )


@router.get("/budget")
def budget_page(request: Request, current_user=Depends(get_current_user), db=Depends(get_db)):
    today = date.today()
    budgets = (
        db.query(Budget)
        .filter(Budget.user_id == current_user.id, Budget.month == today.month, Budget.year == today.year)
        .order_by(Budget.category)
        .all()
    )
    budget_lines = []
    for budget in budgets:
        spent_amount = safe_sum(
            db.query(func.sum(Expense.amount))
            .filter(Expense.user_id == current_user.id)
            .filter(Expense.category == budget.category)
            .filter(extract("month", Expense.expense_date) == today.month)
            .filter(extract("year", Expense.expense_date) == today.year)
            .scalar()
        )
        budget_lines.append(
            {
                "category": budget.category,
                "monthly_limit": float(budget.monthly_limit),
                "spent_amount": spent_amount,
                "remaining": max(float(budget.monthly_limit) - spent_amount, 0.0),
                "percent": round((spent_amount / float(budget.monthly_limit) * 100), 1) if budget.monthly_limit else 0.0,
            }
        )
    return render_page(
        request,
        "Budget",
        current_user,
        "budget.html",
        budgets=budget_lines,
        today=date.today().strftime("%B %Y"),
    )


@router.get("/investments")
def investments_page(request: Request, current_user=Depends(get_current_user), db=Depends(get_db)):
    investments = (
        db.query(Investment)
        .filter(Investment.user_id == current_user.id)
        .order_by(Investment.investment_date.desc())
        .all()
    )
    return render_page(
        request,
        "Investments",
        current_user,
        "investments.html",
        investments=investments,
        today=date.today().strftime("%B %Y"),
    )


@router.get("/savings-goals")
def savings_page(request: Request, current_user=Depends(get_current_user), db=Depends(get_db)):
    goals = (
        db.query(SavingsGoal)
        .filter(SavingsGoal.user_id == current_user.id)
        .order_by(SavingsGoal.target_date)
        .all()
    )
    return render_page(
        request,
        "Savings Goals",
        current_user,
        "savings_goals.html",
        goals=goals,
        today=date.today().strftime("%B %Y"),
    )


@router.get("/reports")
def reports_page(request: Request, current_user=Depends(get_current_user), db=Depends(get_db)):
    return render_page(request, "Reports", current_user, "reports.html", today=date.today().strftime("%B %Y"))


@router.get("/settings")
def settings_page(request: Request, current_user=Depends(get_current_user), db=Depends(get_db)):
    return render_page(request, "Settings", current_user, "settings.html", today=date.today().strftime("%B %Y"))
