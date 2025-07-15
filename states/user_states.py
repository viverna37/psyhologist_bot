from symtable import Class

from aiogram.fsm.state import State, StatesGroup

class RegistrationStates(StatesGroup):
    name = State()
    birthday = State()

class StressTestStates(StatesGroup):
    question_1 = State()
    question_2 = State()
    question_3 = State()
    question_4 = State()
    question_5 = State()
    question_6 = State()
    question_7 = State()
    done = State()

class BuySubscriptionStates(StatesGroup):
    waiting = State()

class CompatibilityStates(StatesGroup):
    date = State()