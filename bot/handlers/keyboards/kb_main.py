from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.handlers.callbacks.callbacks import (Main as MAIN_CB,
                                              Order as ORDER_CB,
                                              Cart as CART_CB)



async def main(price):
    main_menu = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Меню', callback_data=MAIN_CB.main_menu)],
        [InlineKeyboardButton(text='Корзина', callback_data=MAIN_CB.cart)],
    ])

    if price > 249:
        main_menu.inline_keyboard.append(
            [InlineKeyboardButton(text='Оформить заказ', callback_data=MAIN_CB.finish_order)]
        )

    main_menu.inline_keyboard.append(
        [InlineKeyboardButton(text='Связаться с поддержкой', callback_data=MAIN_CB.contacts)]
    )

    return main_menu

async def categories(categories):
    keyboard = InlineKeyboardBuilder()
    for c in categories:
        keyboard.add(InlineKeyboardButton(text=c.name, callback_data=f'{MAIN_CB.select_category} {c.id}'))

    markup = keyboard.adjust(1).as_markup()

    markup.inline_keyboard.append([InlineKeyboardButton(text=f'Назад', callback_data=MAIN_CB.main)])

    return markup

async def dishes(dishes):
    keyboard = InlineKeyboardBuilder()
    for d in dishes:
        keyboard.add(InlineKeyboardButton(text=f'{d.name}', callback_data=f'{MAIN_CB.select_dish} {d.id}'))

    markup = keyboard.adjust(1).as_markup()

    markup.inline_keyboard.append([InlineKeyboardButton(text=f'Назад', callback_data=MAIN_CB.main_menu)])

    return markup


async def cart(price):
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Редактировать', callback_data=CART_CB.cart_edit)],
#        [InlineKeyboardButton(text='Убрать', callback_data=CART_CB.cart_edit_delete)],
    ])

    if price > 250:
        markup.inline_keyboard.append(
            [InlineKeyboardButton(text='Оформить заказ', callback_data=MAIN_CB.finish_order)]
        )

    markup.inline_keyboard.append([InlineKeyboardButton(text=f'Назад', callback_data=MAIN_CB.main)])

    return markup

async def cart_dish_list(dishes, callback_data):
    keyboard = InlineKeyboardBuilder()
    for d in dishes:
        keyboard.add(InlineKeyboardButton(text=f'{d[0].name}', callback_data=f'{callback_data} {d[0].id}'))

    markup = keyboard.adjust(1).as_markup()

    markup.inline_keyboard.append([InlineKeyboardButton(text=f'Назад', callback_data=MAIN_CB.cart)])

    return markup

async def selected_dish(dish_count, back_callback):
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='➖', callback_data=MAIN_CB.select_dish_decrease),
         InlineKeyboardButton(text=str(dish_count), callback_data='nothing'),
         InlineKeyboardButton(text='➕', callback_data=MAIN_CB.select_dish_increase)],
        [InlineKeyboardButton(text='←', callback_data=MAIN_CB.select_dish_left),
         InlineKeyboardButton(text='→', callback_data=MAIN_CB.select_dish_right)],
        [InlineKeyboardButton(text='Назад к оформлению', callback_data=back_callback)]
    ])

    return markup


start_finish_order = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Подтвердить', callback_data=MAIN_CB.accept_order)],
        [InlineKeyboardButton(text='Назад', callback_data=MAIN_CB.main_menu)],
    ])

share_contact = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text='🟩🟩Поделиться контактом🟩🟩', request_contact=True)]
    ],
    one_time_keyboard=True,
    resize_keyboard=True
    )



time_periods = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='20', callback_data=f'{ORDER_CB.time_period} 20'),
         InlineKeyboardButton(text='30', callback_data=f'{ORDER_CB.time_period} 30')],
        [InlineKeyboardButton(text='40', callback_data=f'{ORDER_CB.time_period} 40'),
         InlineKeyboardButton(text='50', callback_data=f'{ORDER_CB.time_period} 50')],
    ])

no_commentary = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Без комментария', callback_data=ORDER_CB.no_commentary)]
    ])


pay_method = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Наличный', callback_data=f'{ORDER_CB.pay_method} Наличный'),
         InlineKeyboardButton(text='Безналичный', callback_data=f'{ORDER_CB.pay_method} Безналичный')]
    ])

back_button = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Назад', callback_data=MAIN_CB.main)],
])