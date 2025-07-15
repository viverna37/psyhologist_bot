from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup

from keyboards.inline_keyboards.ikb import IKB

router = Router()

@router.callback_query(F.data == "invite_friend")
async def invite_friend(callback: CallbackQuery):
    bot_data = await callback.bot.get_me()
    await callback.message.edit_text(f"Вот твоя персональная ссылка для приглашения друзей\nhttps://t.me/{bot_data.username}?start=ref_{callback.from_user.id}", reply_markup=await IKB.User.back_to_main_menu_keyboard())