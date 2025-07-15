from aiogram import Bot, Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.exceptions import TelegramAPIError


class ChannelSubscriptionMiddleware(BaseMiddleware):
    def __init__(self, channel_id: int | str, invite_link: str):
        self.channel_id = channel_id
        self.invite_link = invite_link
        super().__init__()

    async def __call__(self, handler, event, data):
        # Получаем объект бота из данных
        bot: Bot = data.get("bot")

        # Определяем тип события
        if isinstance(event, Message):
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
        else:
            return await handler(event, data)

        try:
            # Проверяем статус подписки
            member = await bot.get_chat_member(chat_id=self.channel_id, user_id=user_id)
            if member.status in ['member', 'administrator', 'creator']:
                return await handler(event, data)

            # Если не подписан - отправляем сообщение
            await self._send_subscription_required(event, bot)
            return
        except TelegramAPIError as e:
            print(f"Ошибка проверки подписки: {e}")
            return await handler(event, data)

    async def _send_subscription_required(self, event, bot: Bot):
        text = (
            "⚠️ Для использования бота необходимо подписаться на наш канал!\n"
            "Подпишитесь и нажмите кнопку проверки:"
        )
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📢 Подписаться", url=self.invite_link)]
        ])

        if isinstance(event, Message):
            await event.answer(text, reply_markup=markup)
        elif isinstance(event, CallbackQuery):
            await event.message.answer(text, reply_markup=markup)