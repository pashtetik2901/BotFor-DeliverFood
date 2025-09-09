from sqlalchemy import BigInteger, String, ForeignKey, Text, DateTime, Numeric
from sqlalchemy.dialects.mssql.information_schema import tables
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

from datetime import datetime

from bot.database.db import Base, engine
from config import DATABASE_URL




class User(Base):
    __tablename__ = 'users'
    tg_id = mapped_column(BigInteger, primary_key=True)
    tg_name:Mapped[str] = mapped_column(String(64), nullable=True)

class Contact(Base):
    __tablename__ = 'contacts'
    id = mapped_column(BigInteger, primary_key=True)
    name = mapped_column(Text, nullable=True)
    contact = mapped_column(Text, nullable=True)


class Category(Base):
    __tablename__ = 'categories'
    id: Mapped[int] = mapped_column( primary_key=True)
    name = mapped_column(Text)



class Dish(Base):
    __tablename__ = 'dishes'
    id: Mapped[int] = mapped_column(primary_key=True)
    id_category: Mapped[int] = mapped_column(ForeignKey('categories.id'))
    name = mapped_column(Text)
    description = mapped_column(Text)
    img_url = mapped_column(Text)
    price = mapped_column(Numeric, nullable=True)
    weight = mapped_column(Numeric, nullable=True)



class Order(Base):
    __tablename__ = 'orders'
    id: Mapped[int] = mapped_column( primary_key=True)
    order_id = mapped_column(Text)
    dishes = mapped_column(Text)
    number = mapped_column(String(16))
    address = mapped_column(Text)
    commentary = mapped_column(Text)
    pay_method = mapped_column(Text)
    price = mapped_column(Text)
    status = mapped_column(Text)


async def db_drop():
    async with engine.begin() as conn:
        tables_to_drop = [Dish.__table__, Category.__table__]

        await conn.run_sync(Base.metadata.drop_all, tables=tables_to_drop)


async def db_create():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)



