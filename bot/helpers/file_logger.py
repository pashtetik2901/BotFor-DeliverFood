import logging
import os
from enum import Enum
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime

from config import BASE_DIR, LOG_ROTATE_DAYS


class LogTypesEnum(Enum):
    INFO = "INFO"
    ERROR = "ERROR"
    WARNING = "WARNING"


# Проверяем существование директории для логов и создаем её, если она не существует
logs_directory = f"{BASE_DIR}/logs"
if not os.path.exists(logs_directory):
    os.makedirs(logs_directory)


# Функция для генерации имени файла с текущей датой и временем
def get_log_file_name(source):
    return os.path.join(logs_directory, f"{source}_{datetime.now().strftime('%Y_%m_%d')}.log")


# Настройка формата логов
log_format = "[%(asctime)s] %(levelname)s %(source)s: %(message)s"

# Словарь для хранения логгеров для каждого source
loggers_cache = {}


def get_or_create_logger(source):
    """
    Получает или создает логгер для указанного source.
    Если логгер уже существует, возвращает его из кэша.
    Если нет, создает новый логгер, добавляет его в кэш и возвращает.
    """
    if source in loggers_cache:
        return loggers_cache[source]

    # Создаем новый логгер
    logger = logging.getLogger(f"dynamic_logger_{source}")
    logger.setLevel(logging.DEBUG)

    # Создаем новый файловый обработчик
    log_file_path = get_log_file_name(source)
    handler = TimedRotatingFileHandler(
        log_file_path,
        when="midnight",
        interval=LOG_ROTATE_DAYS,
        backupCount=5,
        encoding='utf-8'
    )
    handler.setLevel(logging.DEBUG)  # Устанавливаем минимальный уровень логирования
    formatter = logging.Formatter(log_format)
    handler.setFormatter(formatter)

    # Переопределение имени файла при ротации
    def rename_rotated_logs(prefix):
        def namer(default_name):
            # Изменяем имя архивного файла на формат prefix_date_time.log
            base_filename, ext = os.path.splitext(os.path.basename(default_name))
            rotated_time = base_filename.split(".")[1]  # Извлекаем метку времени ротации
            new_filename = f"{prefix}_{rotated_time}{ext}"
            return os.path.join(logs_directory, new_filename)
        return namer

    handler.namer = rename_rotated_logs(source)

    # Добавляем обработчик к логгеру
    logger.addHandler(handler)

    # Добавляем консольный обработчик (по желанию)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_formatter = logging.Formatter("[%(asctime)s] %(levelname)s %(source)s: %(message)s")
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # Добавляем логгер в кэш
    loggers_cache[source] = logger
    return logger


# Функция для записи логов
def log_event(source: str, level: str, message: str):
    """
    Записывает лог с указанным уровнем, сообщением и источником.
    """
    # Получаем или создаем логгер для указанного source
    logger = get_or_create_logger(source)

    # Логируем событие
    logger.log(
        logging.getLevelName(level),
        message,
        extra={"source": source}
    )

# Функции для записи логов
def log_user_event(level: str, user_id: int, message: str):
    # Добавляем контекст пользователя через параметр extra
    log_event(source=f"user_{user_id}", level=level, message=message)


def log_system_event(level: str, message: str):
    # Добавляем контекст системы через параметр extra
    log_event(source="System", level=level, message=message)