from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


class IKB:
    class User:
        @staticmethod
        async def get_main_menu():
            builder = InlineKeyboardBuilder()
            builder.row(
                InlineKeyboardButton(
                    text="Пройти тест на стресс 🤯",
                    callback_data="stress_test"
                ),
                InlineKeyboardButton(
                    text="Карта дня 🃏",
                    callback_data="day_card"
                ), InlineKeyboardButton(
                    text="Поделиться с другом 🤝",
                    callback_data="invite_friend"
                ), InlineKeyboardButton(
                    text="Отзывы 💌",
                    callback_data="review"
                ), InlineKeyboardButton(
                    text="Подсказка на месяц 📆",
                    callback_data="hint_month"
                ), InlineKeyboardButton(
                    text="Совет в ситуации 🔎",
                    callback_data="advice_day"
                ), InlineKeyboardButton(
                    text="Совместимость 💞",
                    callback_data="compatibility"
                ), InlineKeyboardButton(
                    text="Вызвать психолога 🛎️",
                    callback_data="psychologist"
                ), InlineKeyboardButton(
                    text="Личный кабинет 🔐",
                    callback_data="cabinet"
                ),
            )
            builder.adjust(1)
            return builder.as_markup()

        @staticmethod
        async def stress_test_keyboard():
            builder = InlineKeyboardBuilder()
            builder.row(
                InlineKeyboardButton(
                    text="Никогда",
                    callback_data="response_0"
                ),
                InlineKeyboardButton(
                    text="Почти никогда",
                    callback_data="response_1"
                ),
                InlineKeyboardButton(
                    text="Иногда",
                    callback_data="response_2"
                ),
                InlineKeyboardButton(
                    text="Довольно часто",
                    callback_data="response_3"
                ),
                InlineKeyboardButton(
                    text="Очень часто",
                    callback_data="response_4"
                )

            )
            builder.adjust(1)
            return builder.as_markup()

        @staticmethod
        async def cabinet_keyboard():
            builder = InlineKeyboardBuilder()
            builder.row(
                InlineKeyboardButton(
                    text="Купить подписку",
                    callback_data="buy_subscription"
                ),
                InlineKeyboardButton(
                    text="В главное меню",
                    callback_data="back_to_main_menu"
                )
            )
            builder.adjust(1)
            return builder.as_markup()

        @staticmethod
        async def back_to_main_menu_keyboard():
            builder = InlineKeyboardBuilder()
            builder.row(
                InlineKeyboardButton(
                    text="В главное меню",
                    callback_data="back_to_main_menu"
                )
            )
            builder.adjust(1)
            return builder.as_markup()

    class Admin:
        @staticmethod
        async def check_payment(user_id: int, points: list):
            builder = InlineKeyboardBuilder()
            builder.row(
                InlineKeyboardButton(
                    text="Одобрить улучшенный",
                    callback_data=f"approve_1_{user_id}_{points[0]}"),
                InlineKeyboardButton(
                    text="Одобрить премиум",
                    callback_data=f"approve_2_{user_id}_{points[1]}"),
                InlineKeyboardButton(
                    text="Отклонить",
                    callback_data=f"reject_{user_id}"
                )
            )
            builder.adjust(1)
            return builder.as_markup()

        @staticmethod
        async def check_review(user_id: int, points: int):
            builder = InlineKeyboardBuilder()
            builder.row(
                InlineKeyboardButton(
                    text="Одобрить",
                    callback_data=f"review_{user_id}_{points}"),
                InlineKeyboardButton(
                    text="Отклонить",
                    callback_data=f"reviewreject_{user_id}"
                )
            )
            builder.adjust(1)
            return builder.as_markup()

        @staticmethod
        async def admin_main_menu():
            builder = InlineKeyboardBuilder()
            builder.row(
                InlineKeyboardButton(
                    text="📝 Рассылка", callback_data="admin_broadcast"),
                InlineKeyboardButton(
                    text="🖼 Рассылка с картинкой", callback_data="admin_broadcast_photo"
                ),
                InlineKeyboardButton(text="💸 Проверить баланс", callback_data="check_balance"),
                InlineKeyboardButton(text="➖ Списать баланс", callback_data="minus_balance"),
                InlineKeyboardButton(text="➕ Добавить метку", callback_data="add_utm"),
                InlineKeyboardButton(text="📊 Статистика по меткам", callback_data="statistics_utm"),
            )
            builder.adjust(1)
            return builder.as_markup()

        @staticmethod
        async def admin_cancel():
            builder = InlineKeyboardBuilder()
            builder.row(InlineKeyboardButton(text="❌ Отмена", callback_data="admin_back"))
            builder.adjust(1)
            return builder.as_markup()

        @staticmethod
        async def utm_delete_keyboard(data):
            builder = InlineKeyboardBuilder()
            for i in enumerate(data):
                builder.row(
                    InlineKeyboardButton(
                        text=f"{i[0]}", callback_data=f"utm_delete_{i[1].id}")
                )
            builder.adjust(6)
            builder.row(
                InlineKeyboardButton(
                    text="❌ Выйти", callback_data="admin_back"))
            return builder.as_markup()