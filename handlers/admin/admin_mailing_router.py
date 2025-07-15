import asyncio
from datetime import date, timedelta
from typing import Any

from aiogram import Router, F
from aiogram.enums import ContentType
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

import os

from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_dialog import StartMode, DialogManager, Window, Dialog
from aiogram_dialog.widgets.input import TextInput, MessageInput
from aiogram_dialog.widgets.kbd import Radio, Button, Back, Row, ManagedRadio, Calendar
from aiogram_dialog.widgets.text import Const, Format
from dotenv import load_dotenv
from sqlalchemy.util import await_fallback

from config import Config
from database.db import DataBase
from database.models import User, UserSubscription, UserBalance
from keyboards.inline_keyboards.ikb import IKB
from states.admin_states import AdminStates

router = Router()


@router.callback_query(F.data.startswith("approve_"))
async def approve(callback: CallbackQuery, db: DataBase):
    user_id = int(callback.data.split("_")[-2])
    type_subscription = int(callback.data.split("_")[-3])
    points = int(callback.data.split("_")[-1])
    user_balance = await db.get_from_db(UserBalance, filters={"user_id": user_id})
    await db.delete_from_db(UserSubscription, filters={"user_id": user_id}, delete_all=True)
    await db.add_to_db(UserSubscription(user_id=user_id, type_subscription=type_subscription,
                                        date_ended=date.today() + timedelta(days=30), is_active=True))
    await db.update_db(UserBalance, filters={'user_id': user_id},
                       update_data={'balance': int(user_balance[0].balance) - points})
    await callback.bot.send_message(user_id, "Ваша подписка успешно активирована"),
    await callback.message.edit_caption("Подписка выдана")
    await callback.message.edit_reply_markup(None)


@router.callback_query(F.data.startswith("review_"))
async def approve(callback: CallbackQuery, db: DataBase, config: Config):
    user_id = int(callback.data.split("_")[1])
    points = int(callback.data.split("_")[2])

    if callback.message.text:
        await callback.message.bot.send_message(
            chat_id=config.tg_bot.review_channel,
            text=callback.message.text
        )
    elif callback.message.voice:
        await callback.message.bot.send_voice(
            chat_id=config.tg_bot.review_channel,
            voice=callback.message.voice.file_id,
            caption=callback.message.caption
        )
    elif callback.message.video_note:
        await callback.message.bot.send_video_note(
            chat_id=config.tg_bot.review_channel,
            video_note=callback.message.video_note.file_id,
        )

    await callback.message.edit_reply_markup(None)

    user_balance = await db.get_from_db(UserBalance, filters={'user_id': user_id})
    print(user_balance)
    await db.update_db(UserBalance, filters={"user_id": user_id},
                       update_data={"balance": int(user_balance[0].balance) + points})

    await callback.bot.send_message(user_id,
                                    f"Ваш отзыв был проверен и опубликован администрацией, вам начислено {points} баллов")

@router.callback_query(F.data.startswith("reviewreject_"))
async def approve(callback: CallbackQuery, db: DataBase, config: Config):
    user_id = int(callback.data.split("_")[1])
    await callback.bot.send_message(user_id,"Ваш отзыв был отклонен администрацией")
@router.message(F.text == "/admin")
async def admin(message: Message, config):
    if message.from_user.id in config.tg_bot.admin_ids:
        await message.answer("👨‍💻 Админ-панель\nВыберите действие:",
                             reply_markup=await IKB.Admin.admin_main_menu())


@router.callback_query(F.data == "admin_back")
async def start_broadcast(callback: CallbackQuery, state: FSMContext, config):
    await state.clear()
    if callback.from_user.id in config.tg_bot.admin_ids:
        await callback.message.edit_text("👨‍💻 Админ-панель\nВыберите действие:",
                             reply_markup=await IKB.Admin.admin_main_menu())


@router.callback_query(F.data == "admin_broadcast")
async def start_broadcast(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.waiting_for_broadcast_text)
    await callback.message.edit_text(
        "📝 Отправьте текст для рассылки:",
        "ПОСЛЕ ЗАПУСКА РАССЫЛКИ - СО СТОРОНЫ АДМИНИСТРАТОРА НЕ РЕКОМЕНДУЕТСЯ НИЧЕГО НАЖИМАТЬ ПОКА НЕ ПРОЙДЕТ РАССЫЛКА."
        "У рассылки стоит кд - 4 человека в секунду, поэтому надо чууууть-чуть подождать, пока бот не уведомит, что рассылка завершена!"
        # TODO ПОЧИНИТЬ ЭТО
    )


@router.callback_query(F.data == "admin_broadcast_photo")
async def start_broadcast_photo(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.waiting_for_broadcast_image)
    await callback.message.edit_text(
        "🖼 Отправьте картинку для рассылки:"
        "ПОСЛЕ ЗАПУСКА РАССЫЛКИ - СО СТОРОНЫ АДМИНИСТРАТОРА НЕ РЕКОМЕНДУЕТСЯ НИЧЕГО НАЖИМАТЬ ПОКА НЕ ПРОЙДЕТ РАССЫЛКА."
        "У рассылки стоит кд - 4 человека в секунду, поэтому надо чууууть-чуть подождать, пока бот не уведомит, что рассылка завершена!"
        # TODO ПОЧИНИТЬ ЭТО
    )


# Рассылка текста
@router.message(AdminStates.waiting_for_broadcast_text)
async def process_broadcast_text(message: Message, state: FSMContext, db: DataBase):
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer(
            "👨‍💻 Админ-панель\nВыберите действие:",
            reply_markup=await IKB.Admin.admin_main_menu()
        )
        return

    users = await db.get_from_db(User)
    success = 0
    failed = 0

    status_message = await message.answer("⏳ Начинаем рассылку...")

    for user in users:
        try:
            await message.bot.send_message(user.user_id, message.text)
            success += 1
            if success % 5 == 0:
                await status_message.edit_text(
                    f"✉️ Отправлено: {success}\n"
                    f"❌ Ошибок: {failed}"
                )
            await asyncio.sleep(0.07)
        except Exception as e:
            failed += 1

    await status_message.edit_text(
        f"""✅ Рассылка завершена!

📊 Статистика:
✓ Успешно: {success}
❌ Ошибок: {failed}
📱 Всего пользователей: {len(users)}"""
    )

    await state.clear()
    await message.answer(
        "👨‍💻 Админ-панель\nВыберите действие:",
        reply_markup=await IKB.Admin.admin_main_menu()
    )


# Рассылка с картинкой
@router.message(AdminStates.waiting_for_broadcast_image, F.photo)
async def process_broadcast_image(message: Message, state: FSMContext):
    try:
        await state.update_data(photo_id=message.photo[-1].file_id)
        await state.set_state(AdminStates.waiting_for_broadcast_image_text)
        await message.answer(
            "Теперь отправьте текст для рассылки:",
            reply_markup=InlineKeyboardBuilder().button(
                text="❌ Отмена",
                callback_data="admin_back"
            ).as_markup()
        )
    except Exception as e:
        await message.answer("❌ Произошла ошибка при обработке изображения")


@router.message(AdminStates.waiting_for_broadcast_image_text)
async def process_broadcast_image_text(message: Message, state: FSMContext, db: DataBase):
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("Отменено", reply_markup=await IKB.Admin.admin_main_menu())
        return

    state_data = await state.get_data()
    photo_id = state_data.get('photo_id')

    if not photo_id:
        await message.answer(
            "❌ Ошибка: картинка не найдена. Начните заново.",
            reply_markup=await IKB.Admin.admin_main_menu()
        )
        await state.clear()
        return

    users = await db.get_from_db(User)
    success = 0
    failed = 0

    status_message = await message.answer("⏳ Начинаем рассылку...")

    for user in users:
        try:
            await message.bot.send_photo(
                user.user_id,
                photo=photo_id,
                caption=message.text
            )
            success += 1
            if success % 5 == 0:
                await status_message.edit_text(
                    f"✉️ Отправлено: {success}\n"
                    f"❌ Ошибок: {failed}"
                )
            await asyncio.sleep(0.07)
        except Exception as e:
            print(e)
            failed += 1

    await status_message.edit_text(
        f"""✅ Рассылка с картинкой завершена!

📊 Статистика:
✓ Успешно: {success}
❌ Ошибок: {failed}
📱 Всего пользователей: {len(users)}"""
    )

    await state.clear()
    await message.answer(
        "🔔 Рассылка успешно завершена!",
        reply_markup=await IKB.Admin.admin_main_menu()
    )


@router.callback_query(F.data == "check_balance")
async def start_broadcast(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Введи username пользователя или tg_id", reply_markup=await IKB.Admin.admin_cancel())
    await state.set_state(AdminStates.waiting_username)

@router.message(AdminStates.waiting_username)
async def process_broadcast_image_text(message: Message, state: FSMContext, db: DataBase):
    await state.clear()
    user_id = message.text
    try:
        user_id = int(user_id)
        user_data = await db.get_from_db(User, filters={"user_id": user_id})
        user_balance = await db.get_from_db(UserBalance, filters={"user_id": user_id})

    except Exception as e:
        user_data = await db.get_from_db(User, filters={"username": user_id})
        user_balance = await db.get_from_db(UserBalance, filters={"user_id": user_data[0].user_id})

    await message.answer(f"Баланс пользователя {user_data[0].name}: {user_balance[0].balance}\n балл", reply_markup=await IKB.Admin.admin_main_menu())

@router.callback_query(F.data == "minus_balance")
async def start_broadcast(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Введи username пользователя или tg_id", reply_markup=await IKB.Admin.admin_cancel())
    await state.set_state(AdminStates.waiting_username_for_minus)

@router.message(AdminStates.waiting_username_for_minus)
async def process_broadcast_image_text(message: Message, state: FSMContext, db: DataBase):
    await state.set_state(AdminStates.waiting_points)
    user_id = message.text
    try:
        user_id = int(user_id)
        user_data = await db.get_from_db(User, filters={"user_id": user_id})
        user_balance = await db.get_from_db(UserBalance, filters={"user_id": user_id})

    except Exception as e:
        user_data = await db.get_from_db(User, filters={"username": user_id})
        user_balance = await db.get_from_db(UserBalance, filters={"user_id": user_data[0].user_id})

    await message.answer(f"Баланс пользователя {user_data[0].name}: {user_balance[0].balance}\n балл\n\nСколько списать?", reply_markup=await IKB.Admin.admin_cancel())
    await state.update_data(user_id=user_data[0].user_id, user_balance=user_balance[0].balance)

@router.message(AdminStates.waiting_points)
async def process_broadcast_image_text(message: Message, state: FSMContext, db: DataBase):
    data = await state.get_data()
    await state.clear()

    await db.update_db(UserBalance, filters={"user_id": int(data.get("user_id"))}, update_data={"balance": int(data.get("user_balance"))-int(message.text)})

    await message.answer(f"Списал {message.text} баллов", reply_markup=await IKB.Admin.admin_main_menu())