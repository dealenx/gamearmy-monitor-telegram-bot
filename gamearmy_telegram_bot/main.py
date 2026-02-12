import os
import time
import logging
import urllib.parse
from datetime import datetime

import requests
from dotenv import load_dotenv

from gamearmy_telegram_bot import gamearmy_server_players


# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
GAMEARMY_SERVER_ID = os.getenv("GAMEARMY_SERVER_ID")
SERVER_NAME = os.getenv("SERVER_NAME")


def is_telegram_configured() -> bool:
    """Проверить, настроен ли Telegram бот"""
    return bool(TELEGRAM_BOT_TOKEN and CHAT_ID)


def send_telegram_message(message: str) -> bool:
    """
    Отправить сообщение в Telegram
    
    Args:
        message: Текст сообщения
        
    Returns:
        True если сообщение отправлено успешно
    """
    if not is_telegram_configured():
        logger.warning("Telegram бот не настроен (TELEGRAM_BOT_TOKEN или CHAT_ID не указаны). Отправка сообщений отключена.")
        return False
    
    try:
        url = 'https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}'.format(
            TELEGRAM_BOT_TOKEN, 
            CHAT_ID, 
            urllib.parse.quote_plus(message)
        )
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return True
    except requests.RequestException as e:
        logger.error(f"Ошибка отправки в Telegram: {e}")
        return False


def run():
    """Основной цикл мониторинга"""
    if not GAMEARMY_SERVER_ID:
        logger.error("GAMEARMY_SERVER_ID не указан в .env файле. Завершение работы.")
        return
    
    logger.info(f"Запуск мониторинга сервера {SERVER_NAME} (ID: {GAMEARMY_SERVER_ID})")
    
    if not is_telegram_configured():
        logger.warning("Telegram бот не настроен. Уведомления будут выводиться только в лог.")
    
    while True:
        try:
            # Получить текущий список игроков
            current_players = gamearmy_server_players.get_server_players(GAMEARMY_SERVER_ID)
            logger.debug(f"Текущие игроки: {current_players}")

            # Проверить на наличие новых игроков
            new_players = gamearmy_server_players.check_new_players(current_players)

            # Обновить таблицу игроков
            gamearmy_server_players.update_player_table(current_players)

            # Отправить уведомление о новых игроках
            if new_players:
                message = f"Зашли игроки: {', '.join(new_players)} на {SERVER_NAME}"
                logger.info(message)
                send_telegram_message(message)

        except Exception as e:
            logger.error(f"Ошибка в основном цикле: {e}")

        time.sleep(20)


if __name__ == '__main__':
    run()
