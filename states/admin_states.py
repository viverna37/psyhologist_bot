from symtable import Class

from aiogram.fsm.state import State, StatesGroup

class AdminStates(StatesGroup):
    waiting_for_broadcast_text = State()
    waiting_for_broadcast_image = State()
    waiting_for_broadcast_image_text = State()

    waiting_username = State()
    waiting_username_for_minus = State()
    waiting_points = State()