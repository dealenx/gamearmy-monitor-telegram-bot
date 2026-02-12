import os
import logging
import requests
from bs4 import BeautifulSoup
from datetime import datetime

from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker


# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()
GAMEARMY_SERVER_ID = os.getenv("GAMEARMY_SERVER_ID")
DB_FILE_PATH = os.getenv("DB_FILE_PATH")
SERVER_NAME = os.getenv("SERVER_NAME")

# Базовый URL gamearmy.ru
GAMEARMY_BASE_URL = "https://gamearmy.ru"

# Имя базы данных SQLite
db_name = "server_players.db"

# Определение модели игрока
Base = declarative_base()


class Player(Base):
    __tablename__ = 'players'
    id = Column(Integer, primary_key=True)
    name = Column(String)


# Создание двигателя базы данных
engine = create_engine(f'sqlite:///{DB_FILE_PATH}')
Base.metadata.create_all(engine)

# Создание сессии
Session = sessionmaker(bind=engine)
session = Session()


def get_server_players(server_id: str) -> list[str]:
    """
    Получить список игроков с сервера gamearmy.ru
    
    Args:
        server_id: ID сервера на gamearmy.ru (например, "209558")
        
    Returns:
        Список имен игроков на сервере
    """
    try:
        # 1. Загрузить основную страницу для получения ticket
        main_url = f"{GAMEARMY_BASE_URL}/monitoring/{server_id}"
        logger.info(f"Загрузка страницы: {main_url}")
        
        response = requests.get(main_url, timeout=10)
        response.raise_for_status()
        logger.debug(f"Статус ответа: {response.status_code}")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 2. Извлечь ticket из атрибута div.nav_key_line
        nav_key = soup.find('div', class_='nav_key_line')
        if not nav_key:
            logger.warning("Не удалось найти элемент nav_key_line на странице")
            return []
            
        ticket = nav_key.get('ticket')
        if not ticket:
            logger.warning("Не удалось найти атрибут ticket")
            return []
        
        logger.debug(f"Получен ticket: {ticket}")
        
        # 3. Загрузить страницу с игроками
        players_url = f"{GAMEARMY_BASE_URL}/user_stat?ticket={ticket}&id={server_id}"
        logger.info(f"Загрузка списка игроков: {players_url}")
        
        players_response = requests.get(players_url, timeout=10)
        players_response.raise_for_status()
        
        # 4. Парсить таблицу игроков
        players_soup = BeautifulSoup(players_response.content, 'html.parser')
        players = []
        
        for row in players_soup.find_all('tr'):
            # Пропускаем заголовок таблицы
            row_class = row.get('class')
            if row_class and 'head_mon' in row_class:
                continue
                
            cells = row.find_all('td')
            if len(cells) >= 2:
                # Имя игрока во второй ячейке (индекс 1)
                player_name = cells[1].text.strip()
                if player_name:
                    players.append(player_name)
        
        logger.info(f"Найдено {len(players)} игроков на сервере")
        return players
        
    except requests.Timeout:
        logger.error(f"Таймаут при запросе к серверу gamearmy.ru")
        return []
    except requests.RequestException as e:
        logger.error(f"Ошибка при запросе к серверу: {e}")
        return []
    except Exception as e:
        logger.error(f"Неожиданная ошибка при парсинге: {e}")
        return []


def check_new_players(current_players: list[str]) -> list[str]:
    """
    Проверить наличие новых игроков
    
    Args:
        current_players: Текущий список игроков на сервере
        
    Returns:
        Список новых игроков (которых не было раньше)
    """
    new_players = []
    for player in current_players:
        # Проверить, есть ли игрок в базе данных
        existing_player = session.query(Player).filter_by(name=player).first()
        if not existing_player:
            new_players.append(player)
            # Добавить нового игрока
            new_player = Player(name=player)
            session.add(new_player)
            session.commit()
    return new_players


def update_player_table(current_players: list[str]) -> None:
    """
    Обновить таблицу игроков - синхронизировать с текущим состоянием
    
    Args:
        current_players: Текущий список игроков на сервере
    """
    # Удалить существующих игроков из базы данных
    session.query(Player).delete()
    session.commit()

    # Добавить всех текущих игроков в базу данных
    for player in current_players:
        new_player = Player(name=player)
        session.add(new_player)
    session.commit()
    logger.debug(f"Таблица игроков обновлена: {len(current_players)} игроков")
