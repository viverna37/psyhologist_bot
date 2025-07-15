from aiogram import types
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from static.button_texts import ButtonTexts

class RKB:
    @staticmethod
    async def get_customer_main_menu() -> types.ReplyKeyboardMarkup:
        """Главное меню клиента"""
        builder = ReplyKeyboardBuilder()

        builder.button(text=ButtonTexts.customer_main_menu[0])
        builder.button(text=ButtonTexts.customer_main_menu[1])
        # builder.button(text=ButtonTexts.customer_main_menu[2])



        # Оптимальное расположение
        builder.adjust(1)

        return builder.as_markup(
            resize_keyboard=True,
            input_field_placeholder="Выберите раздел..."
        )

    @staticmethod
    async def get_personal_main_menu() -> types.ReplyKeyboardMarkup:
        """Главное меню исполнителя"""
        builder = ReplyKeyboardBuilder()

        builder.button(text=ButtonTexts.executor_main_menu[0])
        builder.button(text=ButtonTexts.executor_main_menu[1])
        builder.button(text=ButtonTexts.executor_main_menu[2])
        builder.button(text=ButtonTexts.executor_main_menu[3])



        # Оптимальное расположение
        builder.adjust(1)

        return builder.as_markup(
            resize_keyboard=True,
            input_field_placeholder="Выберите раздел..."
        )