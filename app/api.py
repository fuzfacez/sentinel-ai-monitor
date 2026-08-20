from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.models import Check, Incident, Monitor
from app.monitoring import check_monitor
from app.schemas import MonitorCreate, MonitorUpdate, model_dict
from app.security import require_admin

router = APIRouter(prefix="/api", dependencies=[Depends(require_admin)])

@router.get("/monitors")
async def monitors(db: AsyncSession = Depends(get_db)):
    rows = (await db.execute(select(Monitor).order_by(Monitor.id))).scalars()
    return [model_dict(x) for x in rows]

@router.post("/monitors", status_code=201)
async def create(payload: MonitorCreate, db: AsyncSession = Depends(get_db)):
    monitor = Monitor(**payload.model_dump(mode="json"), next_check_at=datetime.now(timezone.utc))
    db.add(monitor); await db.commit(); await db.refresh(monitor)
    return model_dict(monitor)

@router.patch("/monitors/{monitor_id}")
async def update(monitor_id: int, payload: MonitorUpdate, db: AsyncSession = Depends(get_db)):
    monitor = await db.get(Monitor, monitor_id)
    if not monitor: raise HTTPException(404, "Monitor not found")
    for key, value in payload.model_dump(exclude_unset=True, mode="json").items(): setattr(monitor, key, value)
    monitor.next_check_at = datetime.now(timezone.utc)
    await db.commit(); await db.refresh(monitor)
    return model_dict(monitor)

@router.delete("/monitors/{monitor_id}", status_code=204)
async def delete(monitor_id: int, db: AsyncSession = Depends(get_db)):
    monitor = await db.get(Monitor, monitor_id)
    if not monitor: raise HTTPException(404, "Monitor not found")
    await db.delete(monitor); await db.commit()

@router.post("/monitors/{monitor_id}/check", status_code=202)
async def check_now(monitor_id: int, db: AsyncSession = Depends(get_db)):
    if not await db.get(Monitor, monitor_id): raise HTTPException(404, "Monitor not found")
    await db.close()
    await check_monitor(monitor_id)
    return {"ok": True}

@router.get("/monitors/{monitor_id}/checks")
async def checks(monitor_id: int, limit: int = 100, db: AsyncSession = Depends(get_db)):
    rows = (await db.execute(select(Check).where(Check.monitor_id == monitor_id).order_by(Check.checked_at.desc()).limit(min(limit, 500)))).scalars()
    return [model_dict(x) for x in rows]

@router.get("/incidents")
async def incidents(limit: int = 100, db: AsyncSession = Depends(get_db)):
    rows = (await db.execute(select(Incident).order_by(Incident.started_at.desc()).limit(min(limit, 500)))).scalars()
    return [model_dict(x) for x in rows]
