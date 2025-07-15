import asyncio
from datetime import date, datetime

from aiogram import Router, F
from aiogram.types import CallbackQuery

from database.db import DataBase
from database.models import UserSubscription, User
from keyboards.inline_keyboards.ikb import IKB
from static.const import month_cards
from static.message_texts import MessageTexts

router = Router()


def calculate_destiny_number(birth_datetime: datetime) -> int:
    def sum_digits(n: int) -> int:
        """Суммирует цифры до получения одной цифры"""
        return n if n < 10 else sum_digits(sum(int(d) for d in str(n)))

    current_year = datetime.now().year
    current_month = datetime.now().month

    return sum_digits(
        sum_digits(birth_datetime.day) +
        sum_digits(birth_datetime.month) +
        sum_digits(current_year) +
        sum_digits(current_month)
    )


@router.callback_query(F.data == "hint_month")
async def hint_month(callback: CallbackQuery, db: DataBase):
    sub_data = await db.get_from_db(UserSubscription, filters={"user_id": callback.from_user.id})
    if sub_data and sub_data[0].is_active:
        user_data = await db.get_from_db(User, filters={"user_id": callback.from_user.id})
        number = calculate_destiny_number(user_data[0].birthday)
        await callback.message.delete()
        await callback.message.answer_photo(photo=month_cards.get(number)[0], caption=month_cards.get(number)[1])
        await callback.message.answer(month_cards.get(number)[2], reply_markup=await IKB.User.back_to_main_menu_keyboard())
    else:
        await callback.answer("У вас нет подписки, приобретите ее в личном кабинете", show_alert=True)
