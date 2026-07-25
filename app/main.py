from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import HTTPException
from app.database import engine, Base
from app.models import User, Income, Expense, Budget, Investment, SavingsGoal  # noqa: F401
from app.routers import api_router

# Create all tables on startup — idempotent, safe on every deploy
print(f"[startup] Tables in metadata: {list(Base.metadata.tables.keys())}")
print(f"[startup] Engine URL: {engine.url}")
Base.metadata.create_all(bind=engine)
print("[startup] create_all() completed")

app = FastAPI(
    title="Personal Finance Management",
    description="A premium fintech-style personal finance dashboard built with FastAPI.",
    version="0.1.0",
)

templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(api_router)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    # Redirect unauthenticated browser requests to /login
    if exc.status_code == 401:
        accept = request.headers.get("accept", "")
        if "text/html" in accept:
            return RedirectResponse(url="/login", status_code=302)
    from fastapi.responses import JSONResponse
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.get("/", include_in_schema=False)
async def root(request: Request):
    return RedirectResponse(url="/login")
