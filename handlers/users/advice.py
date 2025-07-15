import asyncio
import random
from datetime import datetime, date

from aiogram import Router, F
from aiogram.types import CallbackQuery

from database.db import DataBase
from database.models import UserDailyCard, UserSubscription, UserSupportCard
from keyboards.inline_keyboards.ikb import IKB
from static.const import metaphorical_cards
from static.message_texts import MessageTexts

router = Router()


@router.callback_query(F.data == "advice_day")
async def daily_advice_handler(callback: CallbackQuery, db: DataBase):
    user_id = callback.from_user.id
    today = datetime.now().date()

    # Получаем данные о подписке и картах пользователя
    sub_data = await db.get_from_db(UserSubscription, filters={"user_id": user_id})
    user_card_data = await db.get_from_db(UserSupportCard, filters={"user_id": user_id})

    # Проверяем лимиты
    if user_card_data:
        card_record = user_card_data[0]

        # Для подписчиков - неограниченное количество подсказок
        if sub_data and sub_data[0].is_active:
            await send_advice_card(callback, db, user_id, today)
            return

        # Для бесплатных пользователей - проверка лимита
        if card_record.last_card_date == today:
            if card_record.free_uses_today < 2:  # 0, 1, 2 = 3 использования
                await increment_free_uses(db, card_record)
                await send_advice_card(callback, db, user_id, today)
            else:
                await callback.answer(
                    "Вы использовали все 3 бесплатные подсказки на сегодня. Жду вас завтра!",
                    show_alert=True
                )
            return
        else:
            # Новый день - сбрасываем счетчик
            await db.update_db(
                UserSupportCard,
                filters={'user_id': user_id},
                update_data={
                    "last_card_date": today,
                    "free_uses_today": 0
                }
            )
            await send_advice_card(callback, db, user_id, today)
    else:
        # Первое использование - создаем запись
        await db.add_to_db(UserSupportCard(
            user_id=user_id,
            last_card_date=today,
            free_uses_today=0
        ))
        await send_advice_card(callback, db, user_id, today)


async def send_advice_card(callback: CallbackQuery, db: DataBase, user_id: int, today: date):
    """Отправляет карту с подсказкой и обновляет статистику"""
    selected_card = random.choice(metaphorical_cards)

    await callback.message.delete()
    await callback.message.answer_photo(
        photo=selected_card,
        caption="""<b>1.Иногда достаточно одной подсказки. Вот она!</b>

1⃣ <u>Прочти цитату на карте.</u> 
Что она тебе сейчас говорит? Какой в ней совет?
2⃣ <u>Вглядись в изображение.</u> 
Что в нём откликается? Что вызывает напряжение?

Ответ — уже внутри. Эти детали и есть твои ключи 🗝️"""
    )
    await asyncio.sleep(5)
    await callback.message.answer(
        MessageTexts.main_menu_msg,
        reply_markup=await IKB.User.get_main_menu()
    )


async def increment_free_uses(db: DataBase, card_record):
    """Увеличивает счетчик бесплатных использований"""
    await db.update_db(
        UserSupportCard,
        filters={'id': card_record.id},
        update_data={"free_uses_today": card_record.free_uses_today + 1}
    )