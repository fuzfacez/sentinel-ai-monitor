from typing import Any, Literal
from pydantic import BaseModel, Field, HttpUrl

class MonitorCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    url: HttpUrl
    method: Literal["GET", "POST", "PUT", "PATCH", "HEAD"] = "GET"
    headers: dict[str, str] = Field(default_factory=dict)
    body: str | None = None
    expected_status: int = Field(200, ge=100, le=599)
    expected_text: str | None = Field(None, max_length=500)
    timeout_seconds: int = Field(15, ge=1, le=120)
    interval_seconds: int = Field(300, ge=30, le=86400)
    enabled: bool = True

class MonitorUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=120)
    url: HttpUrl | None = None
    method: Literal["GET", "POST", "PUT", "PATCH", "HEAD"] | None = None
    headers: dict[str, str] | None = None
    body: str | None = None
    expected_status: int | None = Field(None, ge=100, le=599)
    expected_text: str | None = Field(None, max_length=500)
    timeout_seconds: int | None = Field(None, ge=1, le=120)
    interval_seconds: int | None = Field(None, ge=30, le=86400)
    enabled: bool | None = None

def model_dict(obj: Any) -> dict:
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}

