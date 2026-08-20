# Sentinel AI — Website Monitoring + AI Incident Analyzer

Готовый self-hosted мониторинг сайтов и API. Проверяет HTTP-код, время ответа, доступность и наличие текста. При первом сбое создаёт инцидент, просит локальный Qwen объяснить вероятную причину и отправляет рекомендации в Telegram. При восстановлении закрывает инцидент и присылает отдельное уведомление.

## Быстрый запуск

Требования: Docker Desktop и (опционально) Ollama с Qwen.

```bash
cp .env.example .env
# В .env обязательно замените ADMIN_TOKEN и POSTGRES_PASSWORD
docker compose up -d --build
```

Откройте `http://localhost:8000/?token=ВАШ_ADMIN_TOKEN`. Swagger API: `http://localhost:8000/docs` (в запросах используйте заголовок `X-Admin-Token`).

Добавить medcampus.uz можно прямо в панели: название `MedCampus`, URL `https://medcampus.uz`, интервал `300`, ожидаемый код `200`.

## Локальный Qwen

На хостовой машине:

```bash
ollama list
ollama pull qwen3.5
ollama serve
```

Укажите точное имя из `ollama list` в `LLM_MODEL`. Docker-контейнер обращается к Ollama через `host.docker.internal:11434`. Если Ollama выключен, мониторинг не ломается: используется встроенный эвристический анализ.

## Telegram

1. Создайте бота через `@BotFather`, запишите токен в `TELEGRAM_BOT_TOKEN`.
2. Узнайте свой chat ID через `@userinfobot`, запишите в `TELEGRAM_CHAT_ID`.
3. Напишите боту `/start` и перезапустите: `docker compose restart app`.

## Что внутри

- FastAPI + защищённый REST API и адаптивная веб-панель;
- APScheduler, параллельные асинхронные HTTP-проверки;
- PostgreSQL: мониторы, проверки и история инцидентов;
- Qwen через Ollama `/api/chat`, JSON-ответ и безопасный fallback;
- Telegram incident/recovery alerts;
- Alembic-миграции, healthchecks и Docker Compose;
- защита панели и API единым admin token.

## API

```bash
curl -X POST http://localhost:8000/api/monitors \
  -H 'Content-Type: application/json' \
  -H 'X-Admin-Token: YOUR_TOKEN' \
  -d '{"name":"MedCampus","url":"https://medcampus.uz","interval_seconds":300}'
```

Endpoints: `GET/POST /api/monitors`, `PATCH/DELETE /api/monitors/{id}`, `POST /api/monitors/{id}/check`, `GET /api/monitors/{id}/checks`, `GET /api/incidents`.

## Продакшен

Поставьте контейнер за HTTPS reverse proxy (Caddy/Nginx), используйте длинный случайный `ADMIN_TOKEN`, не коммитьте `.env`, настройте backup volume `postgres_data`. Запускайте только один экземпляр `app`: APScheduler встроен в процесс. Для горизонтального масштабирования планировщик следует вынести в отдельный worker.

## Проверки

```bash
python -m pip install -e '.[test]'
pytest
docker compose config
```

Лицензия: MIT.

