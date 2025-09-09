from aiogram import types, F, Router
from aiogram.fsm.context import FSMContext
from datetime import datetime
from config import PAYMENT_PROVIDER_TOKEN
import json


payment_router = Router()

@payment_router.pre_checkout_query()
async def pre_checkout_handler(query: types.PreCheckoutQuery):
    await query.bot.answer_pre_checkout_query(query.id, ok=True)



async def pay_callback(message: types.Message, state: FSMContext, cost: int):
    uid = message.from_user.id
    SERVICE_PRICE = cost
    # if callback.data == 'pay':
    #     await callback.answer()
    description, price = 'Опалата заказа', SERVICE_PRICE * 100
    pr = [types.LabeledPrice(label=description, amount=int(price))]
    time_data = datetime.now().strftime('%Y-%m-%d %H-%M-%S')
    pld = f'{message.from_user.id}_{time_data}'
    provider_data = {
        'receipt': {
            "need_email": True,
            "send_email_to_provider": True,
            # 'customer': {
            #     'full_name': callback.from_user.full_name,
            #     'phone': users['phone'],
            #     'email': users['email']
            # },
            'items': [
                {
                    'description': description,
                    'quantity': 1,
                    'amount': {
                        'value': SERVICE_PRICE,
                        'currency': 'RUB'
                    },
                    "vat_code": 1,
                    "payment_mode": "full_payment",
                    "payment_subject": "service"
                }
            ],
            "tax_system_code": 1
        }
    }
    await message.answer_invoice(
        title=description,
        description=description,
        payload=pld,
        provider_token=PAYMENT_PROVIDER_TOKEN,
        currency='RUB',
        prices=pr,
        provider_data=json.dumps(provider_data),
        need_email=True,
        need_phone_number=True,
        send_email_to_provider=True,
        send_phone_number_to_provider=True
    )

