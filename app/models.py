from datetime import datetime
from typing import Optional
from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base

class Monitor(Base):
    __tablename__ = "monitors"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    url: Mapped[str] = mapped_column(String(2048))
    method: Mapped[str] = mapped_column(String(10), default="GET")
    headers: Mapped[dict] = mapped_column(JSONB, default=dict)
    body: Mapped[Optional[str]] = mapped_column(Text)
    expected_status: Mapped[int] = mapped_column(default=200)
    expected_text: Mapped[Optional[str]] = mapped_column(String(500))
    timeout_seconds: Mapped[int] = mapped_column(default=15)
    interval_seconds: Mapped[int] = mapped_column(default=300)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    last_checked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    next_check_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    current_status: Mapped[str] = mapped_column(String(20), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    checks: Mapped[list["Check"]] = relationship(cascade="all, delete-orphan")

class Check(Base):
    __tablename__ = "checks"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    monitor_id: Mapped[int] = mapped_column(ForeignKey("monitors.id", ondelete="CASCADE"), index=True)
    status: Mapped[str] = mapped_column(String(20))
    status_code: Mapped[Optional[int]]
    response_time_ms: Mapped[Optional[int]]
    error: Mapped[Optional[str]] = mapped_column(Text)
    response_excerpt: Mapped[Optional[str]] = mapped_column(Text)
    checked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)

class Incident(Base):
    __tablename__ = "incidents"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    monitor_id: Mapped[int] = mapped_column(ForeignKey("monitors.id", ondelete="CASCADE"), index=True)
    check_id: Mapped[Optional[int]] = mapped_column(ForeignKey("checks.id", ondelete="SET NULL"))
    state: Mapped[str] = mapped_column(String(20), default="open")
    title: Mapped[str] = mapped_column(String(250))
    cause: Mapped[Optional[str]] = mapped_column(Text)
    recommendations: Mapped[Optional[str]] = mapped_column(Text)
    raw_analysis: Mapped[Optional[str]] = mapped_column(Text)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

