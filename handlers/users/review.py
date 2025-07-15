from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, ReplyKeyboardRemove, Message

from config import Config
from keyboards.inline_keyboards.ikb import IKB

router = Router()

@router.callback_query(F.data == "review")
async def review_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("""Оставьте отзыв — и получите бонусы!
Ваш отклик важен и ценен. А ещё — приносит пользу вам:
💬 <b>Текстовый отзыв</b> — 20 бонусов
🎙 <b>Аудиоотзыв</b> — 50 бонусов
🎥 <b>Видеокружок</b> — 70 бонусов

✨ Бонусами можно оплатить до 30% подписки или личной консультации.

📝 Поделиться отзывом можно прямо здесь, просто отправь мне его(любой из форматов). Спасибо за ваш отклик и доверие!
https://t.me/review_knizeva - канал с отзывами""", reply_markup=await IKB.User.back_to_main_menu_keyboard())
    await state.set_state("review")

@router.message(StateFilter("review"))
async def review_handler(message: Message, state: FSMContext, config: Config):
    await state.clear()
    user_id = message.from_user.id
    if message.text:
        await message.bot.send_message(
            chat_id=config.tg_bot.review_admin_channel,
            text=message.text,
            reply_markup=await IKB.Admin.check_review(user_id, 20)
        )
    elif message.voice:
        await message.bot.send_voice(
            chat_id=config.tg_bot.review_admin_channel,
            voice=message.voice.file_id,
            caption=message.caption,
            reply_markup=await IKB.Admin.check_review(user_id, 50)
        )
    elif message.video_note:
        await message.bot.send_video_note(
            chat_id=config.tg_bot.review_admin_channel,
            video_note=message.video_note.file_id,  # Исправлено с video на video_note
            reply_markup=await IKB.Admin.check_review(user_id, 70)  # Добавлен user_id
        )
    else:
        await message.answer("Я не понимаю о чем ты... Пришли мне текст, видеокружок или аудио или выйди в главное меню", reply_markup=await IKB.User.back_to_main_menu_keyboard())

    await message.answer("Получил твой отзыв и отправил его на модерацию, сразу после проверки ты получишь свои балы", reply_markup=await IKB.User.get_main_menu())
