from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardMarkup

from keyboards.inline_keyboards.ikb import IKB

router = Router()

@router.callback_query(F.data == "psychologist")
async def psyhologist_handler(callback: CallbackQuery):
    await callback.message.edit_text("Напиши свой вопрос в личные сообщения @Elizaveta_Kniazevaaa", reply_markup=await IKB.User.back_to_main_menu_keyboard())