import asyncio
from datetime import datetime

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message

from database.db import DataBase
from database.models import UserSubscription, User
from keyboards.inline_keyboards.ikb import IKB
from states.user_states import CompatibilityStates
from static.const import compatibility_card
from static.message_texts import MessageTexts

router = Router()


def calculate_compatibility(date1: datetime, date2: datetime) -> int:
    def sum_to_single_digit(n: int) -> int:
        """Суммирует цифры числа до одной цифры"""
        while n > 9:
            n = sum(int(d) for d in str(n))
        return n

    # Суммируем дни рождения каждого
    day1_sum = sum_to_single_digit(date1.day)
    day2_sum = sum_to_single_digit(date2.day)

    # Общая сумма и приведение к одной цифре
    total = day1_sum + day2_sum
    return sum_to_single_digit(total)


@router.callback_query(F.data == "compatibility")
async def compatibility(callback: CallbackQuery, db: DataBase, state: FSMContext):
    sub_data = await db.get_from_db(UserSubscription, filters={"user_id": callback.from_user.id})
    if sub_data and sub_data[0].type_subscription==2:
        await state.set_state(CompatibilityStates.date)
        await callback.message.edit_text('Введи дату рождения своего партнера в формате <b>ДД.ММ.ГГГГ</b>\n\n<i>* Год можно указать любой</i>', reply_markup=await IKB.User.back_to_main_menu_keyboard())
    else:
        await callback.answer("У вас нет подписки, приобретите ее в личном кабинете", show_alert=True)

@router.message(F.text, StateFilter(CompatibilityStates.date))
async def ffd(message: Message, db: DataBase, state: FSMContext):
    user_data = await db.get_from_db(User, filters={"user_id": message.from_user.id})
    try:
        result = calculate_compatibility(user_data[0].birthday, datetime.strptime(message.text, "%d.%m.%Y"))
        await state.clear()
        await message.delete()
        await message.answer_photo(photo=compatibility_card.get(result)[0], caption=compatibility_card.get(result)[1])
        await asyncio.sleep(5)
        await message.answer("""Более подробный разбор вы можете получить на индивидуальной консультации где можно рассчитать:
— через что эффективно реализовывать ваш союз
— к чему стоит стремиться
— какие уроки и рост заложены в этом контакте
<b>🎁 Вы можете получить бесплатную подсказку от метафорических карт прямо сейчас.
Она поможет взглянуть на ваш союз под другим углом и почувствовать, куда стоит направить внимание.</b>""", reply_markup=await IKB.User.get_main_menu())

        # await message.answer(MessageTexts.main_menu_msg)
    except ValueError:
        await message.edit_text("Введи в корректном формате")