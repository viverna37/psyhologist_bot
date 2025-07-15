import asyncio
import random
from datetime import datetime

from aiogram import Router, F
from aiogram.types import CallbackQuery

from database.db import DataBase
from database.models import UserDailyCard
from keyboards.inline_keyboards.ikb import IKB
from static.const import metaphorical_cards
from static.message_texts import MessageTexts

router = Router()

@router.callback_query(F.data == "day_card")
async def stress_test(callback: CallbackQuery, db: DataBase):
    user_id = callback.from_user.id
    today = datetime.now().date()

    # Получаем пользователя из БД
    user = await db.get_from_db(UserDailyCard, filters={"user_id": user_id})
    try:
        if user[0].last_card_date == today:
            await callback.answer("Сегодня вы уже получали карту дня. Приходите завтра!", show_alert=True)
            return
    except IndexError:
        await db.add_to_db(UserDailyCard(user_id=user_id, last_card_date=datetime.today()))
    # Выбираем случайную карту
    selected_card = random.choice(metaphorical_cards)

    # Обновляем дату в БД
    await db.update_db(UserDailyCard, filters={'user_id': user_id}, update_data={"last_card_date": today})

    await callback.message.delete()
    await callback.message.answer("<b>Ваша карта дня</b>\n(подсказка на день)🃏👇")
    await callback.message.answer_photo(photo=selected_card)
    await asyncio.sleep(5)
    await callback.message.answer(MessageTexts.main_menu_msg, reply_markup=await IKB.User.get_main_menu())
