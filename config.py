import os

from dotenv import load_dotenv
from oauthlib.common import CLIENT_ID_CHARACTER_SET

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Загрузка переменных окружения
if os.path.exists(os.path.join(BASE_DIR, '.env.example')):
    load_dotenv(os.path.join(BASE_DIR, '.env.example'))
else:
    load_dotenv(os.path.join(BASE_DIR, '.env'))

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
DATABASE_URL = f"sqlite+aiosqlite:///{BASE_DIR}/db/{os.getenv('DB_NAME', 'database.sqlite3')}"
GSHEET_URL = os.getenv('GSHEET_URL')
SERVICE_ACCOUNT_JSON = os.getenv('SERVICE_ACCOUNT_PATH')
LOG_ROTATE_DAYS = int(os.getenv('LOG_ROTATE_DAYS', 15))

NO_IMAGE_PATH = 'bot/images/no_image.jpg'

START_HOUR = 12
END_HOUR = 20

PAYMENT_PROVIDER_TOKEN = os.getenv('PAYMENT_PROVIDER_TOKEN')