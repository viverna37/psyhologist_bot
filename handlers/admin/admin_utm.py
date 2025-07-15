from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message, FSInputFile, BufferedInputFile

from database.db import DataBase
from database.models import Utm
from keyboards.inline_keyboards.ikb import IKB

import qrcode
import io
router = Router()

@router.callback_query(F.data == "add_utm")
async def add_utm(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Введи название новой метки", reply_markup=await IKB.Admin.admin_cancel())
    await state.set_state("wait_name_utm")

@router.message(StateFilter("wait_name_utm"))
async def wait_name_utm(message: Message, state: FSMContext, db: DataBase):
    record_id = await db.add_to_db(Utm(name=message.text))

    utm_param = f"utm_{record_id.id}"
    link = f"https://t.me/psy_kniazeva_bot?start={utm_param}"

    # Генерация QR
    qr_img = qrcode.make(link)
    buf = io.BytesIO()
    qr_img.save(buf, format='PNG')
    buf.seek(0)

    qr_bytes = buf.getvalue()
    file = BufferedInputFile(qr_bytes, filename="qr.png")

    await message.answer_photo(file,
                               caption=f"Вот ваша метка:\n\nНазвание: {message.text}\nID: {record_id.id}\nСсылка: {link}")

    await message.answer("👨‍💻 Админ-панель\nВыберите действие:",
                                         reply_markup=await IKB.Admin.admin_main_menu())
    await state.clear()

@router.callback_query(F.data == "statistics_utm")
async def statistics_utm(callback: CallbackQuery, db: DataBase):
    data = await db.get_from_db(Utm)
    mess = ""
    for i in enumerate(data):
        mess += f"{i[0]}. {i[1].name} --- {i[1].statistics}\n"
    await callback.message.edit_text(f"Статистика по меткам\n{mess}\n\nДля удаления метки тыкни кнопку с номером", reply_markup=await IKB.Admin.utm_delete_keyboard(data))

@router.callback_query(F.data.startswith("utm_delete_"))
async def add_utm(callback: CallbackQuery, db: DataBase):
    utm_id = callback.data.split("_")[-1]
    print(utm_id)
    await db.delete_from_db(Utm, filters={"id": int(utm_id)})
    await statistics_utm(callback, db)
