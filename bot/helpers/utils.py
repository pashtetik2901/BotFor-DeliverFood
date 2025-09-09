from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile, InputMediaAnimation, InputMediaPhoto, InputMediaVideo

from aiogram.types import CallbackQuery, Message, FSInputFile

from bot.database import requests as rq, gsheet_requests as gsheet_rq
from bot.database.gsheet_models import *
from datetime import datetime, timedelta, timezone

date_time_regular = r'^(0?[1-9]|[12]\d|3[01])\.(0?[1-9]|1[0-2])\.(\d{4}) ([01]?\d|2[0-3]):([0-5]?\d)$'


orders_to_check = []


async def check_orders(bot):
    orders = orders_to_check
    finished = []
    unfinished = []
    finished, unfinished = await gsheet_rq.check_orders(orders_to_check)
    if len(unfinished) > 0:
        orders_to_check.extend(unfinished)

    if finished != None and len(finished) > 0:
        for f in finished:
            await bot.send_message(chat_id=f.split('_')[0], text=f'Ваш заказ \"{f}\" был успешно выполнен!')
            orders_to_check.remove(f)


async def db_refill():
    await rq.db_drop()
    await rq.db_create()
    await gsheet_rq.check_table()
    await gsheet_rq.dishes_get_all()

async def notify_users(bot):
    users = await rq.users_get_all()
    for u in users:
        try:
            await bot.send_message(u.tg_id ,text='19:40, самое время сделать заказ!')
        except Exception as e:
            print(f'can\'t notify {u.tg_id}')

async def drop_fsm_storage(dispatcher):
    # Получаем список всех пользователей, у которых есть состояние
    await dispatcher.storage.close() # Зависит от реализации хранилища




async def sending_messages(bot, text=None, file_type=None, file=None):
    if file_type != None:
        users = await rq.users_get_all()
        for u in await users:
            try:
                if file_type == 'none':
                    await bot.send_message(u.tg_id, text, parse_mode='html')
                elif file_type == '.jpg':
                    await bot.send_photo(u.tg_id, photo=file, caption=text, parse_mode='html')
                elif file_type == '.mp4':
                    await bot.send_video(u.tg_id, video=file, caption=text, parse_mode='html')
                elif file_type == '.gif':
                    await bot.send_animation(u.tg_id, animation=file, caption=text, parse_mode='html')
            except Exception as e:
                print(f'Cant send message to user {u.tg_id}!!!')

async def detect_file(msg):
    result = True
    file = None
    file_type = None
    try:
        if msg.photo:
            file = msg.photo[-1].file_id
            file_type = '.jpg'
        elif msg.video:
            file = msg.video.file_id
            file_type = '.mp4'
        elif msg.animation:
            file = msg.animation.file_id
            file_type = '.gif'
        else:
            result = False
    except Exception as e:
        result = False

    return (file, file_type, result)


async def generate_media(file_path, file_type, file, caption):
    media = None
    if file_type == '.jpg':
        media = InputMediaPhoto(media=FSInputFile(f'{file_path}{file}{file_type}'), caption=caption, parse_mode='html')
    elif file_type == '.mp4':
        media = InputMediaVideo(media=FSInputFile(f'{file_path}{file}{file_type}'), caption=caption, parse_mode='html')
    elif file_type == '.gif':
        media = InputMediaAnimation(media=FSInputFile(f'{file_path}{file}{file_type}'), caption=caption, parse_mode='html')

    return media

async def send_media(msg: Message, file_path, file_type, file, caption, reply_markup=None):
    temp = None
    fs = FSInputFile(f'{file_path}{file}{file_type}')
    if file_type == '.jpg':
        temp = await msg.answer_photo(photo=fs, caption=caption, parse_mode='html', reply_markup=reply_markup)
    elif file_type == '.mp4':
        temp = await msg.answer_video(video=fs, caption=caption, parse_mode='html', reply_markup=reply_markup)
    elif file_type == '.gif':
        temp = await msg.answer_animation(animation=fs, caption=caption, parse_mode='html', reply_markup=reply_markup)

    return temp


async def has_url(message: Message) -> bool:
    return bool(message.entities and any(e.type == "url" for e in message.entities))

async def get_dish(dishes, id):
    for d in dishes:
        if d[0].id == id:
            return d

    return None


async def get_total_price(dishes):
    sum = 0
    for d in dishes.values():
        sum += d[0].price * d[1]

    return int(sum)

async def get_cart_msg(dishes):
    total_price = await get_total_price(dishes)
    dishes_msg = ('Ваши блюда: \n' +
                  ''.join([f'\n{d[0].name} {int(d[0].price)}₽ (x{d[1]})' for d in dishes.values()]) +
                  f'\n\nИтоговая стоимость: {total_price}₽')
    return (dishes_msg, total_price)


async def get_cart_dishes_list(dishes):
    dishes_list = []
    for d in dishes.items():
        if d[1] > 0:
            dishes_list.append((await rq.dishes_get(d[0]), d[1]))

    return dishes_list


async def is_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False