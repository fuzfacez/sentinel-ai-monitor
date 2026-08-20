import html
import httpx
from app.config import settings

async def send_telegram(text: str) -> bool:
    if not settings.telegram_bot_token or not settings.telegram_chat_id:
        return False
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.post(
            f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage",
            json={"chat_id": settings.telegram_chat_id, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True},
        )
        response.raise_for_status()
    return True

def incident_message(name: str, url: str, cause: str, actions: str) -> str:
    return f"🚨 <b>{html.escape(name)} недоступен</b>\n{html.escape(url)}\n\n<b>Возможная причина:</b> {html.escape(cause)}\n\n<b>Рекомендуемые действия:</b>\n{html.escape(actions)}"

def recovery_message(name: str, url: str) -> str:
    return f"✅ <b>{html.escape(name)} восстановлен</b>\n{html.escape(url)}"

