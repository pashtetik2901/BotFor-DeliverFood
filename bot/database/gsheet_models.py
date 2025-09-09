from sqlalchemy import BigInteger, String, ForeignKey, Text, DateTime, Numeric
from sqlalchemy.dialects.mssql.information_schema import tables
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

from datetime import datetime


class Category():
    def __init__(self, id:int, name:str):
        self.id = id
        self.name = name

class Dish():
    def __init__(self, id:int, name:str, category_id:int, weight:int, price):
        self.id = id
        self.name = name
        self.category_id = category_id
        self.weight = weight
        self.price = price

class Contacts():
    def __init__(self, id:int, name:str, contact:str):
        self.id = id
        self.name = name
        self.contact = contact

#'ID', "Состав заказа", "Номер заказчика", "Адрес", "Время доставки", "Комментарий", "Способ оплаты", "Статус"
class Order():
    def __init__(self, id:str, date:str, dishes:[], number:str, address:str, time:str, commentary:str, pay_method:str, price, status:str):
        self.id = id
        self.date = date
        self.dishes = dishes
        self.number = number
        self.address = address
        self.time = time
        self.commentary = commentary
        self.pay_method = pay_method
        self.price = price
        self.status = status




