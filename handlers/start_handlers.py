import datetime
import random

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from database.db import DataBase
from database.models import *
from states.user_states import RegistrationStates
from static.const import metaphorical_cards
from static.message_texts import MessageTexts
from keyboards.inline_keyboards.ikb import IKB

router = Router()


#
# @router.message(F.photo)
# async def get_file_id(message: Message):
#     file = message.photo[-1].file_id
#     print(file)

@router.message(F.text.startswith("/start"))
async def start(message: Message, db: DataBase, state: FSMContext):
    await state.clear()
    payload = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None

    user = await db.get_from_db(User, filters={"user_id": message.from_user.id})
    if not user:
        await db.add_to_db(User(
            user_id=message.from_user.id,
            username=message.from_user.username or "Unknown"
        ))
        await db.add_to_db(UserBalance(user_id=message.from_user.id))

        # Добавим запись в реферальную таблицу, если параметр ref_*
        if payload and payload.startswith("ref_"):
            try:
                referrer_id = int(payload.split("_")[1])
                # Проверим, что реферер существует в БД
                referrer = await db.get_from_db(User, filters={"user_id": referrer_id})
                if referrer:
                    await db.add_to_db(Referral(
                        referrer_id=referrer[0].user_id,
                        referred_id=message.from_user.id,
                        timestamp=datetime.utcnow()
                    ))
                pin = await message.answer_photo(photo="AgACAgIAAxkBAAIBrGhxRkpm8XPxLkM4ZnpO8uO71NeGAAKm9jEbyB-RS38ZS_hIbjSVAQADAgADeQADNgQ", caption="За переход дарим вам сертификат")
                await message.bot.pin_chat_message(message.chat.id, pin.message_id)

                balance_data = await db.get_from_db(UserBalance, filters={"user_id": int(referrer_id)})
                await db.update_db(UserBalance, filters={"user_id": int(referrer_id)}, update_data={"balance": balance_data[0].balance + 50})
                await message.bot.send_message(referrer_id, f"У вас новый рефферал @{message.from_user.username}\n <b>Вам доступно +50 баллов на баланс</b>", reply_markup=await IKB.User.get_main_menu())

            except (IndexError, ValueError):
                pass
        elif payload.startswith("utm_"):
            try:
                utm_id = payload.split("_")[1]
                utm_data = await db.get_from_db(Utm, filters={"id": int(utm_id)})
                await db.update_db(Utm, filters={"id": int(utm_id)}, update_data={"statistics": int(utm_data[0].statistics) + 1})
            except (IndexError, ValueError):
                pass


    # Повторный запрос пользователя
    user = await db.get_from_db(User, filters={"user_id": message.from_user.id})
    user = user[0]
    if user.name and user.birthday:
        await message.answer(MessageTexts.start_msg, reply_markup=await IKB.User.get_main_menu(), disable_web_page_preview=True)
    else:
        await message.answer_photo(
            photo="AgACAgIAAxkBAAIDPWh2WUQN3VllURQINZJvfkkKWlkTAAK9-TEbY7axS9G1I5BQ33LOAQADAgADeQADNgQ")
        await message.answer(MessageTexts.start_msg, disable_web_page_preview=True)
        await state.set_state(RegistrationStates.name)
        await message.answer("Введи своё имя ⬇️")


@router.message(F.text, StateFilter(RegistrationStates.name))
async def process_name(message: Message, db: DataBase, state: FSMContext):
    name = message.text.strip()
    if len(name) < 2 or not name.isalpha():
        return await message.answer("Имя должно содержать только буквы и быть не короче 2 символов. Попробуй еще раз.")

    await db.update_db(User, filters={"user_id": message.from_user.id}, update_data={"name": name})
    await message.answer(
        f"Приятно познакомиться, {name}!\nТеперь введи свою дату рождения в формате <b>ДД.ММ.ГГГГ</b>\n<b>✅Пример:</b> 07.10.2025")
    await state.set_state(RegistrationStates.birthday)


@router.message(F.text, StateFilter(RegistrationStates.birthday))
async def process_birthday(message: Message, db: DataBase, state: FSMContext):
    try:
        birthday = datetime.strptime(message.text.strip(), "%d.%m.%Y").date()
        today = datetime.now().date()

        if birthday > today:
            return await message.answer("Дата рождения не может быть в будущем. Попробуй еще раз.")
        if (today - birthday).days > 365 * 150:  # больше 150 лет
            return await message.answer("Проверь дату рождения, кажется введена нереалистичная дата.")

        await db.update_db(User, filters={"user_id": message.from_user.id},
                           update_data={"birthday": birthday})
        await message.answer_photo(photo=random.choice(metaphorical_cards))
        await message.answer("Спасибо! Рад знакомству с тобой, лови свою метафорическую карту",
                                   reply_markup=await IKB.User.get_main_menu())
        await state.clear()
    except ValueError:
        await message.answer("Неверный формат даты. Пожалуйста, введи дату в формате <b>ДД.ММ.ГГГГ</b>\n<b>Пример:</b> 07.10.2025")

@router.callback_query(F.data == "back_to_main_menu")
async def start(callback: CallbackQuery, db: DataBase, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(MessageTexts.main_menu_msg, reply_markup=await IKB.User.get_main_menu())
