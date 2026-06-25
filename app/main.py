from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.database import engine
from app.models import Base  # noqa: F401
from app.routers import api_router

app = FastAPI(
    title="Personal Finance Management",
    description="A premium fintech-style personal finance dashboard built with FastAPI.",
    version="0.1.0",
)

templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(api_router)

Base.metadata.create_all(bind=engine)


@app.get("/", include_in_schema=False)
async def root(request: Request):
    return RedirectResponse(url="/login")
