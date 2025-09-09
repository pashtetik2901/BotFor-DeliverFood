from aiogram.fsm.state import StatesGroup, State

class OrderStates(StatesGroup):
    contact = State()
    address = State()
    order = State()
    commentary = State()
