from asyncio import sleep

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message, FSInputFile, InputMediaDocument, InputMediaPhoto, InputMediaVideo
from aiogram.fsm.context import FSMContext
from pydantic_core.core_schema import none_schema

import bot.database.gsheet_requests as rq
import bot.helpers.utils as U

from bot.handlers.keyboards import kb_client
from bot.handlers.states.client_states import *
from datetime import datetime


router = Router()



