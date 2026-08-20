import hmac
from fastapi import Header, HTTPException, Query
from app.config import settings

async def require_admin(x_admin_token: str | None = Header(None), token: str | None = Query(None)):
    supplied = x_admin_token or token or ""
    if not settings.admin_token or not hmac.compare_digest(supplied, settings.admin_token):
        raise HTTPException(401, "Invalid admin token")

