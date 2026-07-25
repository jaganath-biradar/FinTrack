import logging
import logging.config
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import HTTPException
from app.database import engine, Base
from app.models import User, Income, Expense, Budget, Investment, SavingsGoal  # noqa: F401
from app.routers import api_router

# Configure logging — shows in Render logs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# Create all tables on startup
logger.info(f"[startup] Tables in metadata: {list(Base.metadata.tables.keys())}")
logger.info(f"[startup] Engine URL: {engine.url}")
try:
    Base.metadata.create_all(bind=engine)
    logger.info("[startup] create_all() completed successfully")
except Exception as e:
    logger.error(f"[startup] create_all() FAILED: {e}", exc_info=True)

app = FastAPI(
    title="Personal Finance Management",
    version="0.1.0",
)

templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(api_router)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == 401:
        accept = request.headers.get("accept", "")
        if "text/html" in accept:
            return RedirectResponse(url="/login", status_code=302)
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.url}: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/", include_in_schema=False)
async def root(request: Request):
    return RedirectResponse(url="/login")
