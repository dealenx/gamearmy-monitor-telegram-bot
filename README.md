# GameArmy Telegram Bot

Telegram бот для мониторинга игровых серверов на gamearmy.ru. Отправляет уведомления когда игроки заходят на сервер.

## Требования

- [devbox](https://www.jetify.com/devbox) или Python 3.10+ с [uv](https://docs.astral.sh/uv/)

## Установка

### С devbox (рекомендуется)

```bash
devbox run install
```

### Без devbox

```bash
uv sync
```

## Настройка

```bash
cp .env.example .env
```

Заполнить переменные в `.env`:

```env
# ID сервера на gamearmy.ru (из URL: https://gamearmy.ru/monitoring/209558)
GAMEARMY_SERVER_ID=209558

# Telegram Bot (оставить пустыми для работы без отправки в Telegram)
TELEGRAM_BOT_TOKEN=your_bot_token
CHAT_ID=your_chat_id
# Адрес Telegram Bot API (для зеркала/local Bot API server); пусто = https://api.telegram.org
TELEGRAM_API_URL=

# База данных SQLite
DB_FILE_PATH=server_players.db

# Название сервера для отображения в сообщениях
SERVER_NAME=My Server
```

## Запуск

### С devbox

```bash
devbox run start
```

### Без devbox

```bash
uv run gamearmy-bot
```

### С Docker

```bash
docker run -d --name gamearmy-bot --restart unless-stopped \
  -e GAMEARMY_SERVER_ID=209558 \
  -e TELEGRAM_BOT_TOKEN=... -e CHAT_ID=... \
  -e TELEGRAM_API_URL=https://api.telegram.org \
  -e SERVER_NAME="West UT3" -e DB_FILE_PATH=/data/server_players.db \
  -v gamearmy-data:/data \
  ghcr.io/dealenx/gamearmy-monitor-telegram-bot:latest
```

### Docker Compose / Portainer

```bash
docker compose up -d
```

Вставить в **Portainer → Stacks → Add stack → Web editor** (то же, что
[`docker-compose.yml`](docker-compose.yml)):

```yaml
services:
  bot:
    image: ghcr.io/dealenx/gamearmy-monitor-telegram-bot:latest
    container_name: gamearmy-bot
    restart: unless-stopped
    environment:
      # ID сервера из URL https://gamearmy.ru/monitoring/209558
      GAMEARMY_SERVER_ID: "${GAMEARMY_SERVER_ID:-209558}"
      SERVER_NAME: "${SERVER_NAME:-West UT3}"
      # Пустые значения = бот только пишет в лог
      TELEGRAM_BOT_TOKEN: "${TELEGRAM_BOT_TOKEN:-}"
      CHAT_ID: "${CHAT_ID:-}"
      # Зеркало Telegram API (например http://telegram-bot-api:8081); по умолчанию официальный
      TELEGRAM_API_URL: "${TELEGRAM_API_URL:-https://api.telegram.org}"
      DB_FILE_PATH: /data/server_players.db
    volumes:
      - data:/data

volumes:
  data:
```

В Portainer при создании стека есть два места для переменных:

1. **Environment variables** — ввести по одной вручную, либо кнопка **Load variables from .env file** и
   загрузить файл. Значения подставляются в `${...}` в compose.
2. **`env_file: [stack.env]`** в сервисе — тогда в Portainer загруженный `.env` монтируется как
   `stack.env`, и переменные попадают в контейнер целиком, без `${...}` в compose
   (не работает на Docker Swarm).

Значения для этого стека:

```env
GAMEARMY_SERVER_ID=209558
SERVER_NAME=West UT3
TELEGRAM_BOT_TOKEN=123456:AA...
CHAT_ID=-1001234567890
# Необязательно: зеркало Bot API вместо https://api.telegram.org
TELEGRAM_API_URL=
```

`TELEGRAM_API_URL` указывает альтернативный Bot API (например зеркало или
[local Bot API server](https://github.com/tdlib/telegram-bot-api)): бот обращается к
`{TELEGRAM_API_URL}/bot<token>/sendMessage`. Пустое значение = официальный `https://api.telegram.org`.

Без этих переменных запустятся значения по умолчанию (server `209558`, Telegram отключён).
Если задавать переменные вообще не хочется — можно захардкодить значения прямо в блок `environment`
и не создавать `.env`. Локально `docker compose up -d` сам подхватит `.env` из корня репозитория.
Образ из GHCR (`linux/amd64` и `linux/arm64`), SQLite в именованном volume `data`, автоперезапуск.

Готовый образ собирается в GitHub Actions (`.github/workflows/docker.yml`) и публикуется в GHCR
на каждый push в `main` (теги `latest`, `main`, `sha-<commit>`) и на теги `v*` (тег версии).
Пакет публичный — pull без логина; если снова сделаете приватным, нужен `docker login ghcr.io`.

## Как это работает

1. Бот каждые 20 секунд проверяет список игроков на сервере через gamearmy.ru
2. Если появились новые игроки - отправляет уведомление в Telegram
3. Если Telegram не настроен - выводит информацию только в лог
