import asyncio
import logging
import time
from datetime import datetime, timedelta, timezone
import httpx
from sqlalchemy import select
from app.analyzer import analyze
from app.config import settings
from app.db import SessionLocal
from app.models import Check, Incident, Monitor
from app.telegram import incident_message, recovery_message, send_telegram

log = logging.getLogger(__name__)

async def execute_check(monitor: Monitor) -> Check:
    started = time.perf_counter()
    code = elapsed = None
    error = excerpt = None
    status = "down"
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=monitor.timeout_seconds) as client:
            response = await client.request(monitor.method, monitor.url, headers=monitor.headers or {}, content=monitor.body)
            elapsed = round((time.perf_counter() - started) * 1000)
            code = response.status_code
            excerpt = response.text[:2000]
            ok = code == monitor.expected_status and (not monitor.expected_text or monitor.expected_text in response.text)
            status = "up" if ok else "down"
            if not ok: error = f"Expected HTTP {monitor.expected_status}" + (f" and text '{monitor.expected_text}'" if monitor.expected_text else "")
    except Exception as exc:
        elapsed = round((time.perf_counter() - started) * 1000)
        error = f"{type(exc).__name__}: {exc}"[:2000]
    return Check(monitor_id=monitor.id, status=status, status_code=code, response_time_ms=elapsed, error=error, response_excerpt=excerpt)

async def check_monitor(monitor_id: int):
    async with SessionLocal() as db:
        monitor = await db.get(Monitor, monitor_id)
        if not monitor or not monitor.enabled: return
        previous = monitor.current_status
        check = await execute_check(monitor)
        db.add(check)
        now = datetime.now(timezone.utc)
        monitor.current_status = check.status
        monitor.last_checked_at = now
        monitor.next_check_at = now + timedelta(seconds=monitor.interval_seconds)
        await db.flush()
        if check.status == "down" and previous != "down":
            analysis = await analyze(monitor, check)
            incident = Incident(monitor_id=monitor.id, check_id=check.id, title=f"{monitor.name} недоступен", cause=analysis["cause"], recommendations=analysis["recommendations"], raw_analysis=analysis["raw"])
            db.add(incident)
            await db.commit()
            try: await send_telegram(incident_message(monitor.name, monitor.url, incident.cause or "", incident.recommendations or ""))
            except Exception: log.exception("Telegram incident notification failed")
        elif check.status == "up" and previous == "down":
            result = await db.execute(select(Incident).where(Incident.monitor_id == monitor.id, Incident.state == "open").order_by(Incident.started_at.desc()).limit(1))
            incident = result.scalar_one_or_none()
            if incident:
                incident.state = "resolved"; incident.resolved_at = now
            await db.commit()
            try: await send_telegram(recovery_message(monitor.name, monitor.url))
            except Exception: log.exception("Telegram recovery notification failed")
        else:
            await db.commit()

async def dispatch_due_checks():
    now = datetime.now(timezone.utc)
    async with SessionLocal() as db:
        result = await db.execute(select(Monitor.id).where(Monitor.enabled.is_(True), (Monitor.next_check_at.is_(None)) | (Monitor.next_check_at <= now)))
        ids = list(result.scalars())
        if ids:
            await db.execute(Monitor.__table__.update().where(Monitor.id.in_(ids)).values(next_check_at=now + timedelta(seconds=settings.check_tick_seconds * 2)))
            await db.commit()
    if ids:
        await asyncio.gather(*(check_monitor(mid) for mid in ids), return_exceptions=True)

