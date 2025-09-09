from sqlalchemy import event
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from config import *

from sqlalchemy.ext.asyncio import async_sessionmaker

Base = declarative_base()


def get_db_url():
    # Если используется sqlite
    return DATABASE_URL

def get_base():
    return Base

# Создание движка и фабрики сессий
engine = create_async_engine(
    url=get_db_url(),
    #echo=DATABASE_URL == True,  # Включает логирование SQL-запросов (для отладки)
    pool_pre_ping=True  # Проверяет соединение перед использованием
)


async_session = async_sessionmaker(engine)

# Настройка колляции NOCASE при подключении к базе данных
@event.listens_for(engine.sync_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """
    Настройка подключения к SQLite.
    """
    # Устанавливаем необходимые PRAGMA
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA encoding = 'UTF-8';")
    cursor.execute("PRAGMA case_sensitive_like = OFF;")  # Для регистронезависимого LIKE
    cursor.close()


