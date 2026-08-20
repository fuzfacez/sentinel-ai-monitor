# Установка на VPS без домена

Самый безопасный вариант без домена — не публиковать панель в интернет. Sentinel работает на VPS круглосуточно и отправляет Telegram-уведомления, а панель открывается через зашифрованный SSH-туннель.

Подойдёт чистый сервер Ubuntu 22.04/24.04 с 1 ГБ RAM, публичным IPv4 и SSH-доступом. Открывать порт `8000` в firewall не нужно.

## 1. Установка на сервере

Подключитесь к серверу:

```bash
ssh root@SERVER_IP
```

Установите Git, клонируйте проект и подготовьте конфигурацию:

```bash
apt-get update && apt-get install -y git
git clone https://github.com/fuzfacez/sentinel-ai-monitor.git /opt/sentinel-ai
cd /opt/sentinel-ai
cp deploy/server.env.example .env
nano .env
```

Замените пять значений: `ADMIN_TOKEN`, два одинаковых пароля в `POSTGRES_PASSWORD` и `DATABASE_URL`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`. Для генерации секретов можно выполнить два раза:

```bash
openssl rand -hex 32
```

Запустите автоматическую установку:

```bash
chmod +x deploy/*.sh
./deploy/install.sh
```

Скрипт установит Docker, если его нет, соберёт контейнеры, применит миграции и включит автозапуск после перезагрузки.

## 2. Открытие панели с компьютера

На своём компьютере выполните, не закрывая терминал:

```bash
ssh -N -L 8000:127.0.0.1:8000 root@SERVER_IP
```

Откройте:

```text
http://localhost:8000/?token=ВАШ_ADMIN_TOKEN
```

Соединение до VPS зашифровано SSH. Порт панели снаружи закрыт, поэтому домен и HTTPS-сертификат не требуются.

## Обслуживание

```bash
cd /opt/sentinel-ai
./deploy/update.sh                 # обновить код
sudo docker compose logs -f app   # посмотреть логи
sudo docker compose restart app   # перезапустить
./deploy/backup.sh                 # backup PostgreSQL
```

Для ежедневного бэкапа:

```bash
(crontab -l 2>/dev/null; echo '15 3 * * * /opt/sentinel-ai/deploy/backup.sh >> /var/log/sentinel-backup.log 2>&1') | crontab -
```

## Qwen на сервере

Qwen не требуется для определения `UP/DOWN` и Telegram-уведомлений. На обычном недорогом VPS оставьте `LLM_ENABLED=false`: встроенный анализ объясняет DNS, connection, HTTP 4xx/5xx и таймауты. Локальная модель на вашем ноутбуке недоступна удалённому VPS, когда ноутбук выключен. Позже Qwen можно установить непосредственно на мощный сервер или подключить внешний OpenAI-совместимый API.
