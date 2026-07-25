import os
import logging
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.database import engine, Base
from app.models import User, Income, Expense, Budget, Investment, SavingsGoal  # noqa: F401
from app.routers import api_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ── Table creation ────────────────────────────────────────────
logger.info(f"[startup] Tables in metadata: {list(Base.metadata.tables.keys())}")
logger.info(f"[startup] Engine URL: {engine.url}")
try:
    Base.metadata.create_all(bind=engine)
    logger.info("[startup] create_all() completed successfully")
except Exception as e:
    logger.error(f"[startup] create_all() FAILED: {e}", exc_info=True)

# ── Rate limiter ──────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])

# ── Security headers middleware ───────────────────────────────
_IS_PROD = os.getenv("RENDER", "") != ""

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        if _IS_PROD:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com https://unpkg.com https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data:; "
            "connect-src 'self';"
        )
        return response

# ── App ───────────────────────────────────────────────────────
app = FastAPI(title="FinTrack", version="1.0.0")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SecurityHeadersMiddleware)

templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(api_router)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == 401:
        if "text/html" in request.headers.get("accept", ""):
            return RedirectResponse(url="/login", status_code=302)
    if exc.status_code == 403:
        if "text/html" in request.headers.get("accept", ""):
            # Redirect back to the originating form page
            referer = request.headers.get("referer", "")
            if "/register" in referer:
                return RedirectResponse(url="/register?error=forbidden", status_code=302)
            return RedirectResponse(url="/login?error=forbidden", status_code=302)
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.url}: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/login")
