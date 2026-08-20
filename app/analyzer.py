import json
import httpx
from app.config import settings
from app.models import Check, Monitor

def fallback_analysis(check: Check) -> dict[str, str]:
    error = check.error or ""
    if "Name or service not known" in error or "nodename nor servname" in error:
        cause, action = "DNS-имя не разрешается.", "Проверьте DNS-записи, домен и настройки резолвера."
    elif "Connect" in error:
        cause, action = "Сервис не принимает соединение или недоступен по сети.", "Проверьте процесс приложения, порт, firewall и балансировщик."
    elif check.status_code and check.status_code >= 500:
        cause, action = "Приложение вернуло серверную ошибку.", "Проверьте логи приложения, БД и зависимые сервисы в момент сбоя."
    elif check.status_code in (401, 403):
        cause, action = "Запрос отклонён системой авторизации.", "Проверьте токен, права и правила WAF."
    elif check.response_time_ms:
        cause, action = "Ответ не соответствует условию проверки.", "Проверьте содержимое ответа и производительность зависимостей."
    else:
        cause, action = "Сайт недоступен, точная причина не определена.", "Проверьте сеть, DNS, TLS и логи приложения."
    return {"cause": cause, "recommendations": action, "raw": "Локальный эвристический анализ"}

async def analyze(monitor: Monitor, check: Check) -> dict[str, str]:
    fallback = fallback_analysis(check)
    if not settings.llm_enabled:
        return fallback
    prompt = f"""Ты SRE. Проанализируй инцидент, не выдумывай факты. Ответь строго JSON с ключами cause и recommendations на русском языке. Recommendations — короткий нумерованный список.\nСервис: {monitor.name}\nURL: {monitor.url}\nМетод: {monitor.method}\nОжидался HTTP: {monitor.expected_status}\nПолучен HTTP: {check.status_code}\nВремя: {check.response_time_ms} ms\nОшибка: {check.error}\nФрагмент ответа: {check.response_excerpt}"""
    headers = {"Authorization": f"Bearer {settings.llm_api_key}"} if settings.llm_api_key else {}
    try:
        async with httpx.AsyncClient(timeout=settings.llm_timeout_seconds) as client:
            response = await client.post(f"{settings.llm_base_url.rstrip('/')}/api/chat", headers=headers, json={
                "model": settings.llm_model, "stream": False, "format": "json",
                "messages": [{"role": "user", "content": prompt}],
                "options": {"temperature": 0.2},
            })
            response.raise_for_status()
            content = response.json()["message"]["content"]
            parsed = json.loads(content)
            return {"cause": str(parsed["cause"]), "recommendations": str(parsed["recommendations"]), "raw": content}
    except Exception as exc:
        fallback["raw"] = f"LLM unavailable ({type(exc).__name__}); локальный эвристический анализ"
        return fallback

