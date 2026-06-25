from fastapi import APIRouter
from app.routers import auth, dashboard, income, expenses, budgets, investments, savings, reports, pages

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(dashboard.router)
api_router.include_router(income.router)
api_router.include_router(expenses.router)
api_router.include_router(budgets.router)
api_router.include_router(investments.router)
api_router.include_router(savings.router)
api_router.include_router(reports.router)
api_router.include_router(pages.router)
