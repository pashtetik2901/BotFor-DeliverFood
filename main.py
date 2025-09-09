import logging
import re
import json
import time
import asyncio
import traceback

from aiogram import F, Bot, Dispatcher
# from aiogram.dispatcher.middlewares import data
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.event import dispatcher

import bot.helpers.utils as U
from config import *
from bot.handlers.h_main import router as h_main_router
from bot.handlers.h_admin import router as h_admin_router
from bot.handlers.h_client import router as h_client_router
from bot.handlers.payment import payment_router
from bot.database import gsheet_requests as gsheet_rq, requests as rq
from bot.helpers.scheduler import scheduler
from datetime import datetime, timedelta

# Настроим логирование
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(TELEGRAM_TOKEN)
dp = Dispatcher()


async def main():
    print('trying to get started')


    await rq.db_drop()
    await rq.db_create()
    await gsheet_rq.check_table()
    await gsheet_rq.dishes_get_all()
    #await gsheet_rq.total_dishes()
    #categories = await rq.categories_get_all()
    #ga = await rq.giveaways_get_by_id(1)

    # запуск планировшика
    scheduler.start()

    # job для проверки статуса заказов
    scheduler.add_job(U.check_orders, trigger='interval', seconds=30,timezone='Europe/Moscow',
                      kwargs={'bot': bot})

    scheduler.add_job(gsheet_rq.total_dishes, trigger='cron', hour=20, minute=5, timezone='Europe/Moscow')

    scheduler.add_job(U.db_refill, trigger='cron', hour=11, minute=55, timezone='Europe/Moscow')
    #scheduler.add_job(U.drop_fsm_storage, trigger='cron', hour=20, minute=18, timezone='Europe/Moscow',
    #                  kwargs={'dispatcher': dp})
    scheduler.add_job(U.notify_users, trigger='cron', hour=19, minute=40, timezone='Europe/Moscow',
                      kwargs={'bot': bot})
    #scheduler.add_job(U.finish_giveaway, trigger='date',
    #                  run_date=datetime.now() + timedelta(seconds=15),
    #                  kwargs={'bot': bot, 'ga': ga})

    dp.include_router(h_main_router)
    dp.include_router(h_admin_router)
    dp.include_router(h_client_router)
    dp.include_router(payment_router)
    await dp.start_polling(bot, )


if __name__ == "__main__":
    asyncio.run(main())