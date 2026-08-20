import logging
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from app.api import router
from app.config import settings
from app.db import SessionLocal
from app.models import Incident, Monitor
from app.monitoring import dispatch_due_checks
from app.security import require_admin

logging.basicConfig(level=settings.log_level)
scheduler = AsyncIOScheduler(timezone="UTC")

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.add_job(dispatch_due_checks, "interval", seconds=settings.check_tick_seconds, max_instances=1, coalesce=True, id="monitor-dispatch")
    scheduler.start()
    yield
    scheduler.shutdown(wait=False)

app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)
app.include_router(router)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.get("/health")
async def health(): return {"status": "ok"}

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, _: None = Depends(require_admin)):
    async with SessionLocal() as db:
        monitors = list((await db.execute(select(Monitor).order_by(Monitor.id))).scalars())
        incidents = list((await db.execute(select(Incident).order_by(Incident.started_at.desc()).limit(20))).scalars())
    return templates.TemplateResponse(request, "dashboard.html", {"monitors": monitors, "incidents": incidents, "token": request.query_params.get("token", ""), "app_name": settings.app_name})

