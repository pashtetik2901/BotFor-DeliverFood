import bot.database.gsheet_requests as gsheet_rq
import bot.database.requests as rq
import bot.handlers.keyboards.kb_main as kb_main

from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile, CallbackQuery, InputMediaPhoto
from aiogram.fsm.context import FSMContext


from bot.handlers.callbacks.callbacks import (Main as MAIN_CB, Order as ORDER_CB, Cart as CART_CB)
from bot.handlers.states.main_states import *
from bot.database.gsheet_models import *
from datetime import datetime, timedelta, timezone
from config import START_HOUR, END_HOUR, NO_IMAGE_PATH

from bot.handlers.payment import pay_callback

import bot.handlers.messages.main_messages as MAIN_MSG

import bot.helpers.utils as U
from bot.handlers.keyboards.kb_main import dishes

router = Router()


@router.message(CommandStart())
async def cmd_start(msg: Message, state:FSMContext):
    today = datetime.now(timezone.utc) + timedelta(hours=3)
    if today.hour <START_HOUR or today.hour >= END_HOUR:
        await msg.answer(text=MAIN_MSG.Main.not_a_time)
        return

    await state.clear()
    data = await state.get_data()
    await rq.users_add(msg.from_user.id, msg.from_user.username)
    total_price = await check_state_data(msg, state, data)
    await msg.answer(text=MAIN_MSG.Main.greetings, reply_markup=await kb_main.main(total_price))

@router.callback_query(F.data == MAIN_CB.main)
async def cmd_start_from_callback(cb: CallbackQuery, state:FSMContext):
    data = await state.get_data()
    await rq.users_add(cb.from_user.id, cb.from_user.username)
    total_price = await check_state_data(cb.message, state, data)
    await cb.message.edit_text(text=MAIN_MSG.Main.greetings, reply_markup=await kb_main.main(total_price))



@router.callback_query(F.data == MAIN_CB.contacts)
async def contacts(cb: CallbackQuery, state:FSMContext):
    data = await state.get_data()
    contacts = await gsheet_rq.contacts_get_all()
    msg_text = 'Контакты:\n'+''.join([f'\n{c.name}:\n{c.contact}' for c in contacts])
    await cb.message.edit_text(text=msg_text, reply_markup=kb_main.back_button)



@router.callback_query(F.data == MAIN_CB.main_menu)
async def categories(cb: CallbackQuery, state:FSMContext):
    data = await state.get_data()
    categories = await rq.categories_get_all()
    await cb.message.edit_text(text=MAIN_MSG.Main.categories, reply_markup=await kb_main.categories(categories))


@router.callback_query(F.data.startswith(MAIN_CB.select_category))
async def select_category(cb: CallbackQuery, state:FSMContext):
    data = await state.get_data()
    id_category = cb.data.split()[1]
    dishes_by_category = list(await rq.dishes_get_all_by_id_category(id_category))
    dishes = [i.id for i in dishes_by_category]
    await state.update_data(dishes=dishes)

    try:
        await cb.message.edit_text(text=MAIN_MSG.Main.categories, reply_markup=await kb_main.dishes(dishes_by_category))
    except Exception:
        await cb.message.delete()
        await cb.message.answer(text=MAIN_MSG.Main.categories, reply_markup=await kb_main.dishes(dishes_by_category))


@router.callback_query(F.data.startswith(MAIN_CB.select_dish))
async def select_dish(cb: CallbackQuery, state:FSMContext):
    data = await state.get_data()
    dishes = data['dishes']
    order = data['order']
    selected_dish_id = int(cb.data.split()[1])
    dish_id = dishes.index(selected_dish_id)
    await state.update_data(current_dish_id=dish_id)
    await state.update_data(is_cart=False)

    dish = await rq.dishes_get(selected_dish_id)
    current_dish_amount_in_cart = order.dishes.get(selected_dish_id, (None,0))[1]

    msg_text = f'<b>{dish.name}</b>\n\n{dish.description}\n\nВес: {int(dish.weight)} гр.\nЦена: {int(dish.price)} ₽'
    msg_reply_markup = await kb_main.selected_dish(current_dish_amount_in_cart, f'{MAIN_CB.select_category} {dish.id_category}')

    try:
        await cb.message.edit_media(InputMediaPhoto(media=dish.img_url, caption=msg_text, parse_mode='HTML'),
                                    reply_markup=msg_reply_markup)
    except Exception:
        await cb.message.edit_media(InputMediaPhoto(media=FSInputFile(NO_IMAGE_PATH), caption=msg_text, parse_mode='HTML'),
                                    reply_markup=msg_reply_markup)


@router.callback_query(F.data.in_([MAIN_CB.select_dish_right, MAIN_CB.select_dish_left,
                                   MAIN_CB.select_dish_increase, MAIN_CB.select_dish_decrease]))
async def select_dish_action(cb: CallbackQuery, state:FSMContext):
    data = await state.get_data()
    dishes = data['dishes']
    order = data['order']
    current_dish_id = data['current_dish_id']
    new_current_dish_id = current_dish_id
    dish = None
    amount_edit = False

    if cb.data == MAIN_CB.select_dish_right:
        new_current_dish_id = 0 if current_dish_id > len(dishes) - 2 else current_dish_id + 1

    elif cb.data == MAIN_CB.select_dish_left:
        new_current_dish_id = len(dishes)-1 if current_dish_id < 1 else current_dish_id - 1

    elif cb.data == MAIN_CB.select_dish_increase:
        amount_edit = True
        dish = await rq.dishes_get(dishes[new_current_dish_id])
        d_count = order.dishes.get(dishes[new_current_dish_id], (None, 0))[1]
        order.dishes[dishes[new_current_dish_id]] = (dish, d_count + 1)


    elif cb.data == MAIN_CB.select_dish_decrease:
        amount_edit = True
        dish = await rq.dishes_get(dishes[new_current_dish_id])
        d_count = order.dishes.get(dishes[new_current_dish_id],  (None, 0))[1]
        if d_count < 1:
            result = order.dishes.pop(dishes[new_current_dish_id], None)
            if result == None:
                await cb.answer(text='Нельзя уменьшать ниже 0!')
                return
        else:
            order.dishes[dishes[new_current_dish_id]] = (dish, d_count - 1)
            if order.dishes[dishes[new_current_dish_id]][1] == 0:
                order.dishes.pop(dishes[new_current_dish_id], None)


    await state.update_data(current_dish_id=new_current_dish_id, order=order)

    if dish == None:
        dish = await rq.dishes_get(dishes[new_current_dish_id])

    current_dish_amount_in_cart = order.dishes.get(dishes[new_current_dish_id], (None, 0))[1]
    msg_text = f'<b>{dish.name}</b>\n\n{dish.description}\n\nВес: {int(dish.weight)} гр.\nЦена: {int(dish.price)} ₽'
    msg_reply_markup = await kb_main.selected_dish(current_dish_amount_in_cart, (
                                        f'{CART_CB.cart_edit}'
                                        if data['is_cart']
                                        else f'{MAIN_CB.select_category} {dish.id_category}'))

    if amount_edit:
        await cb.message.edit_caption(caption=msg_text,
                                      parse_mode='HTML',
                                      reply_markup=msg_reply_markup)

    else:
        try:
            await cb.message.edit_media(media=InputMediaPhoto(media=dish.img_url, caption=msg_text, parse_mode='HTML'),
                                        reply_markup=msg_reply_markup)
        except Exception:
            await cb.message.edit_media(media=InputMediaPhoto(media=FSInputFile(NO_IMAGE_PATH), caption=msg_text, parse_mode='HTML'),
                                        reply_markup=msg_reply_markup)











@router.callback_query(F.data == MAIN_CB.cart)
async def cart(cb: CallbackQuery, state:FSMContext):
    data = await state.get_data()
    dishes_msg, total_price = await U.get_cart_msg(data['order'].dishes)
    await cb.message.edit_text(text=dishes_msg, reply_markup=await kb_main.cart(total_price))




@router.callback_query(F.data == CART_CB.cart_edit)
async def cart_edit(cb: CallbackQuery, state:FSMContext):
    data = await state.get_data()
    dishes_msg, total_price = await U.get_cart_msg(data['order'].dishes)
    await state.update_data(is_cart=True)
    try:
        await cb.message.edit_text(text=dishes_msg, reply_markup=await kb_main.cart_dish_list(data['order'].dishes.values(), CART_CB.cart_edit_select))
    except Exception:
        await cb.message.delete()
        await cb.message.answer(text=dishes_msg, reply_markup=await kb_main.cart_dish_list(data['order'].dishes.values(), CART_CB.cart_edit_select))



@router.callback_query(F.data.startswith(CART_CB.cart_edit_select))
async def cart_edit_select(cb: CallbackQuery, state:FSMContext):
    data = await state.get_data()
    order = data['order']
    dishes = list(order.dishes.keys())
    selected_dish_id = int(cb.data.split()[1])
    dish_id = dishes.index(selected_dish_id)
    await state.update_data(dishes=dishes)
    await state.update_data(current_dish_id=dish_id)

    dish = await rq.dishes_get(selected_dish_id)
    dish_in_cart = order.dishes.get(selected_dish_id)[1]

    msg_text = f'<b>{dish.name}</b>\n\n{dish.description}\n\nВес: {int(dish.weight)} гр.\nЦена: {int(dish.price)} ₽'
    msg_reply_markup = await kb_main.selected_dish(dish_in_cart, f'{CART_CB.cart_edit}')

    try:
        await cb.message.edit_media(InputMediaPhoto(media=dish.img_url, caption=msg_text, parse_mode='HTML'),
                                    reply_markup=msg_reply_markup)
    except Exception:
        await cb.message.edit_media(InputMediaPhoto(media=FSInputFile(NO_IMAGE_PATH), caption=msg_text, parse_mode='HTML'),
                                    reply_markup=msg_reply_markup)



@router.callback_query(F.data == CART_CB.cart_edit_delete)
async def cart_delete(cb: CallbackQuery, state:FSMContext):
    data = await state.get_data()
    await cb.message.edit_text(text='Используйте кнопки снизу для удаления блюд', reply_markup=await kb_main.cart_dish_list(data['order'].dishes.values(), CART_CB.delete_dish))

@router.callback_query(F.data.startswith(CART_CB.delete_dish))
async def delete_dish(cb: CallbackQuery, state:FSMContext):
    data = await state.get_data()
    order = data['order']
    dish_id = int(cb.data.split()[1])
    tmp = order.dishes.pop(dish_id, None)

    await state.update_data(order=order)
    await cb.message.edit_text(text='Используйте кнопки снизу для удаления блюд',
                               reply_markup=await kb_main.cart_dish_list(order.dishes.values(), CART_CB.delete_dish))


@router.callback_query(F.data == MAIN_CB.finish_order)
async def finish_order_start(cb: CallbackQuery, state:FSMContext):
    today = datetime.now(timezone.utc) + timedelta(hours=3)
    if today.hour <START_HOUR or today.hour >= END_HOUR:
        await cb.message.answer(text=MAIN_MSG.Main.not_a_time)
        return


    data = await state.get_data()
    dishes_msg, total_price = await U.get_cart_msg(data['order'].dishes)
    await cb.message.edit_text(text=dishes_msg, reply_markup=kb_main.start_finish_order)


@router.callback_query(F.data == MAIN_CB.accept_order)
async def finish_order_1_contact(cb: CallbackQuery, state:FSMContext):
    data = await state.get_data()
    await cb.message.delete()
    await state.set_state(OrderStates.contact)
    msg = await cb.message.answer(text='Нажмите на кнопку под полем ввода сообщения, чтобы поделиться своим телефоном',
                                  reply_markup=kb_main.share_contact)
    await state.update_data(menu=msg)

@router.message(OrderStates.contact)
async def finish_order_2_address(msg: Message, state:FSMContext):
    data = await state.get_data()
    await msg.delete()
    await data['menu'].delete()
    if msg.contact:
        order = data['order']
        order.number = msg.contact.phone_number

        await state.set_state(OrderStates.address)
        msg = await msg.answer(text='Напишите свой адрес')
        await state.update_data(order=order, menu=msg)
    else:
        msg = await msg.answer(text='❗️❗️❗️Вы не поделились своим телефоном')
        await state.update_data(menu=msg)

@router.message(OrderStates.address)
async def finish_order_3_commentary_start(msg: Message, state:FSMContext):
    data = await state.get_data()
    await msg.delete()
    #await data['menu'].delete()
    if msg.text:
        order = data['order']
        order.address = msg.text
        await state.update_data(order=order)
        await state.set_state(OrderStates.commentary)
        await data['menu'].edit_text(text='Введите комментарий к заказу.', reply_markup=kb_main.no_commentary)
    else:
        msg = await msg.answer(text='❗️❗️❗️Вы не ввели свой адрес')
        await state.update_data(menu=msg)

#@router.callback_query(OrderStates.address)
#async def finish_order_4_commentary_start(cb: CallbackQuery, state:FSMContext):
#    data = await state.get_data()
#    time_period = int(cb.data.split()[1])
#    order = data['order']
#    order.time = time_period
#    await state.update_data(order=order, menu=cb.message)
#    await state.set_state(OrderStates.commentary)
#    await cb.message.edit_text(text='Введите комментарий к заказу.', reply_markup=kb_main.no_commentary)

@router.callback_query(F.data == ORDER_CB.no_commentary)
async def finish_order_4_1_no_commentary(cb: CallbackQuery, state:FSMContext):
    data = await state.get_data()
    order = data['order']
    order.commentary = ''
    await state.update_data(order=order)
    await state.set_state(None)
    await data['menu'].edit_text(text='Выберите способ оплаты', reply_markup=kb_main.pay_method)

@router.message(OrderStates.commentary)
async def finish_order_4_2_commentary(msg: Message, state:FSMContext):
    data = await state.get_data()
    await msg.delete()

    if msg.text:
        order = data['order']
        order.commentary = msg.text
        await state.update_data(order=order)
        await state.set_state(None)
        await data['menu'].edit_text(text='Выберите способ оплаты', reply_markup=kb_main.pay_method)
    else:
        await data['menu'].edit_text(text='❗️❗️❗️Вы не ввели комментарий')


@router.callback_query(F.data.startswith(ORDER_CB.pay_method) )
async def finish_order_5_pay_method(cb: CallbackQuery, state:FSMContext):
    today = datetime.now(timezone.utc) + timedelta(hours=3)
    if today.hour <START_HOUR or today.hour >= END_HOUR:
        await cb.message.answer(text=MAIN_MSG.Main.not_a_time)
        return


    data = await state.get_data()

    today = datetime.now(timezone.utc) + timedelta(hours=3)
    order_date = today.strftime("%d.%m.%Y")

    order = data['order']
    order.pay_method = cb.data.split()[1]

    if order.pay_method == 'Наличный':
        order.price = await U.get_total_price(order.dishes)
        order.date = order_date
        await state.clear()
        await gsheet_rq.order_add(order)
        U.orders_to_check.append(order.id)
        await data['menu'].edit_text(text=f'Ваш заказ был успешно создан. \n Номер вашего заказа: {order.id}')

    elif order.pay_method == 'Безналичный':
        order.price = await U.get_total_price(order.dishes)

        await pay_callback(cb.message, state, order.price)

@router.message(F.successful_payment)
async def successful_payment_handler(message: Message, state: FSMContext):
    await message.answer(text='Вы успешно оплатили заказ!')

    data = await state.get_data()

    today = datetime.now(timezone.utc) + timedelta(hours=3)
    order_date = today.strftime("%d.%m.%Y")

    order = data['order']

    order.price = await U.get_total_price(order.dishes)
    order.date = order_date
    await state.clear()
    await gsheet_rq.order_add(order)
    U.orders_to_check.append(order.id)
    # await data['menu'].edit_text(text=f'Ваш заказ был успешно создан. \n Номер вашего заказа: {order.id}')
    await message.answer(text=f'Ваш заказ был успешно создан. \n Номер вашего заказа: {order.id}')








async def check_state_data(msg: Message, state: FSMContext, data):
    total_price = None
    if data.get('order') == None:
        today = datetime.now(timezone.utc) + timedelta(hours=3)
        order_id = f'{msg.from_user.id}_{today.strftime("%d%m%Y_%H%M%S")}'
        await state.update_data(order=Order(order_id, None, {}, None, None, None, None, None, 0, 'Создан')
                                )

        total_price = 0
    else:
        total_price = await U.get_total_price(data['order'].dishes)

    return total_price