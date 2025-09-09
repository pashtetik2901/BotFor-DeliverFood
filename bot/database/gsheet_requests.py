from datetime import timezone, timedelta

import gspread

import bot.database.requests as rq

from aiogram.types import giveaway

from bot.database.gsheet_models import *
from sqlalchemy import select, update, delete, and_
from config import SERVICE_ACCOUNT_JSON, GSHEET_URL
from gspread import Client, Spreadsheet, Worksheet
from gspread.utils import ValueInputOption, ValidationConditionType


ws_orders = "Заказы"
ws_dishes = "Блюда"
ws_contacts = "Контакты"
ws_total_dishes_by_date = "Итоги по дате"


async def is_table_exists():
    try:
        gc: Client = gspread.service_account(SERVICE_ACCOUNT_JSON)
        sh: Spreadsheet = gc.open_by_url(GSHEET_URL)
        ws: Worksheet = sh.sheet1
        ws.update_acell('A1', "")
        return True
    except Exception as e:
        return False


async def check_table():
    try:
        gc: Client = gspread.service_account(SERVICE_ACCOUNT_JSON)
        sh: Spreadsheet = gc.open_by_url(GSHEET_URL)

        # проверка на наличие листа "Заказы"
        try:
            ws: Worksheet = sh.worksheet(ws_orders)
        except Exception as e:
            ws = sh.add_worksheet(ws_orders, 10, 1)
            ws.append_row(['ID', "Дата заказа", "Состав заказа", "Номер заказчика", "Адрес", "Комментарий", "Способ оплаты", "Цена", "Статус"])
            ws.add_validation("I", ValidationConditionType.one_of_list, ['Создан','Выполнен'])

        # проверка на наличие листа "Блюда"
        try:
            ws: Worksheet = sh.worksheet(ws_dishes)
        except Exception as e:
            ws = sh.add_worksheet(ws_dishes, 10, 1)
            ws.append_row(['Категория', "Название", "Описание", "Картинка", "Стоимость", "Вес"])

        # проверка на наличие листа "Итоги по дате"
        try:
            ws: Worksheet = sh.worksheet(ws_total_dishes_by_date)
        except Exception as e:
            ws = sh.add_worksheet(ws_total_dishes_by_date, 10, 1)
            ws.append_row(['Дата', "Всего заказов", "Всего блюд"])


        # проверка на наличие листа "Контакты"
        try:
            ws: Worksheet = sh.worksheet(ws_contacts)
        except Exception as e:
            ws = sh.add_worksheet(ws_contacts, 10, 1)
            ws.append_row(['ID', "Название", "Контакт"])

        return True
    except Exception as e:
        return False



async def dishes_get_all():
    try:
        gc: Client = gspread.service_account(SERVICE_ACCOUNT_JSON)
        sh: Spreadsheet = gc.open_by_url(GSHEET_URL)

        ws: Worksheet = sh.worksheet(ws_dishes)

        table_rows = ws.get_all_values()
        table_values = table_rows[1: len(table_rows)]

        for r in table_values:
            await rq.categories_add(r[0])
            id_category = (await rq.categories_get_by_name(r[0])).id
            await rq.dishes_add(id_category, r[1], r[2], r[3], r[4], r[5])

        return True
    except Exception as e:
        return False

async def dishes_get_by_category_id(category_id):
    try:
        gc: Client = gspread.service_account(SERVICE_ACCOUNT_JSON)
        sh: Spreadsheet = gc.open_by_url(GSHEET_URL)

        dishes = []
        ws: Worksheet = sh.worksheet(ws_dishes)

        table_rows = ws.get_all_values()
        table_values = table_rows[1: len(table_rows)]

        for r in table_values:
            if r[2] == category_id:
                dishes.append(Dish(r[0], r[1], r[2], r[3], r[4]))

        return dishes
    except Exception as e:
        return None

async def contacts_get_all():
    try:
        gc: Client = gspread.service_account(SERVICE_ACCOUNT_JSON)
        sh: Spreadsheet = gc.open_by_url(GSHEET_URL)

        contacts = []
        ws: Worksheet = sh.worksheet(ws_contacts)

        table_rows = ws.get_all_values()
        table_values = table_rows[1: len(table_rows)]

        for r in table_values:
            contacts.append(Contacts(r[0], r[1], r[2]))

        return contacts
    except Exception as e:
        return None

async def order_add(order):
    try:
        gc: Client = gspread.service_account(SERVICE_ACCOUNT_JSON)
        sh: Spreadsheet = gc.open_by_url(GSHEET_URL)

        dishes = []
        ws: Worksheet = sh.worksheet(ws_orders)

        dishes_str = '\n'.join([f'{d[0].name} x{d[1]}' for d in order.dishes.values()])
        ws.append_row([order.id, order.date, dishes_str, order.number, order.address, order.commentary, order.pay_method, order.price, order.status])

        return dishes
    except Exception as e:
        return None

async def check_orders(orders):
    try:
        gc: Client = gspread.service_account(SERVICE_ACCOUNT_JSON)
        sh: Spreadsheet = gc.open_by_url(GSHEET_URL)

        dishes = []
        ws: Worksheet = sh.worksheet(ws_orders)

        finished = []
        unfinished = []

        for o in orders:
            cell = ws.find(o, in_column=1)
            if ws.cell(cell.row, 9).value == "Выполнен":
                finished.append(o)

        cells = ws.findall("Создан", in_column=9)
        for c in cells:
            value = ws.cell(c.row, 1).value
            if value not in orders:
                unfinished.append(value)

        return (finished, unfinished)
    except Exception as e:
        return (None, None)

async def total_dishes():
    try:
        gc: Client = gspread.service_account(SERVICE_ACCOUNT_JSON)
        sh: Spreadsheet = gc.open_by_url(GSHEET_URL)

        dishes = []
        ws: Worksheet = sh.worksheet(ws_orders)

        today = datetime.now(timezone.utc) + timedelta(hours=3)
        order_date = today.strftime("%d.%m.%Y")

        dishes = {}

        cells = ws.findall(order_date, in_column=2)
        for c in cells:
            order_dishes = ws.cell(c.row, 3).value.split('\n')
            for d in order_dishes:
                len_d = len(d)
                space_id = d.rfind(' ')
                dish_name = d[:space_id]
                dish_count = int(d[space_id+2:len_d])

                dish_count_in_list = dishes.get(dish_name, (None, 0))[1]
                dishes[dish_name] = (dish_name, dish_count_in_list + dish_count)


        ws: Worksheet = sh.worksheet(ws_total_dishes_by_date)

        total_dishes_str = '\n'.join([f'{d[0]} x{d[1]}' for d in sorted(dishes.values(), key=lambda i: i[1], reverse=True)])
        ws.append_row([order_date, len(cells), total_dishes_str])
    except Exception as e:
        print('Не удалось подключиться к таблице')



