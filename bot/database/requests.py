from datetime import timedelta

from aiogram.types import giveaway

from bot.database.db import async_session
from bot.database.models import *
from sqlalchemy import select, update, delete, and_, func


async def db_fill():
    pass



# - - - - - - - - - - - - - - - - - - - -
#                U S E R S
# - - - - - - - - - - - - - - - - - - - -
async def users_add(tg_id, tg_name):
    async with async_session() as session:
        item = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not item:
            session.add(User(tg_id=tg_id, tg_name=tg_name))
            await session.commit()


async def users_get(tg_id):
    async with async_session() as session:
        return await session.scalar(select(User).where(User.tg_id == tg_id))

async def users_get_by_tg_name(tg_name):
    async with async_session() as session:
        return await session.scalar(select(User).where(User.tg_name == tg_name))

async def users_get_all():
    async with async_session() as session:
        return await session.scalars(select(User))



# - - - - - - - - - - - - - - - - - - - -
#        C A T E G O R I E S
# - - - - - - - - - - - - - - - - - - - -
async def categories_add(name):
    async with async_session() as session:
        item = await session.scalar(select(Category).where(Category.name == name))

        if not item:
            session.add(Category(name=name))
            await session.commit()


async def categories_get(id):
    async with async_session() as session:
        return await session.scalar(select(Category).where(Category.id == id))

async def categories_get_by_name(name):
    async with async_session() as session:
        return await session.scalar(select(Category).where(Category.name == name))

async def categories_get_all():
    async with async_session() as session:
        return await session.scalars(select(Category))





# - - - - - - - - - - - - - - - - - - - -
#               D I S H E S
# - - - - - - - - - - - - - - - - - - - -
async def dishes_add(id_category, name, description, img_url, price, weight):
    async with async_session() as session:
        item = await session.scalar(select(Dish).where(Dish.name == name))

        if not item:
            session.add(Dish(id_category=id_category, name=name, description=description, img_url=img_url, price=price, weight=weight))
            await session.commit()

async def dishes_get(id):
    async with async_session() as session:
        return await session.scalar(select(Dish).where(Dish.id == id))

async def dishes_get_by_name(id_category):
    async with async_session() as session:
        return await session.scalar(select(Dish).where(Dish.id_category == id_category))

async def dishes_get_all():
    async with async_session() as session:
        return await session.scalars(select(Dish))

async def dishes_get_all_by_id_category(id_category):
    async with async_session() as session:
        return await session.scalars(select(Dish).where(Dish.id_category == id_category))





# - - - - - - - - - - - - - - - - - - - -
#               O R D E R S
# - - - - - - - - - - - - - - - - - - - -
async def orders_add(order_id, dishes, number, address, commentary, pay_method, price, status):
    async with async_session() as session:
        item = await session.scalar(select(Order).where(Order.order_id == order_id))

        if not item:
            session.add(Order(order_id=order_id, dishes=dishes, number=number, address=address, commentary=commentary, pay_method=pay_method, price=price, status=status))
            await session.commit()

async def orders_get(id):
    async with async_session() as session:
        return await session.scalar(select(Order).where(Order.id == id))

async def orders_get_by_order_id(order_id):
    async with async_session() as session:
        return await session.scalar(select(Order).where(Order.order_id == order_id))

async def orders_get_all():
    async with async_session() as session:
        return await session.scalars(select(Order))


