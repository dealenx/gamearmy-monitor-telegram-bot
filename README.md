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

## Как это работает

1. Бот каждые 20 секунд проверяет список игроков на сервере через gamearmy.ru
2. Если появились новые игроки - отправляет уведомление в Telegram
3. Если Telegram не настроен - выводит информацию только в лог
