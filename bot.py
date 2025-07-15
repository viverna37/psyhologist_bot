import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio

from config import load_config
from database.db import DataBase
# Настройка логгирования SQLAlchemy
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)  # Скрываем SQL-запросы

# Опционально: настройка общего логгирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


async def main():
    # Инициализация бота с новым синтаксисом
    config = load_config()

    bot = Bot(
        token=os.getenv("BOT_TOKEN"),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    dp["config"] = config
    dp["db"] = DataBase()

    # import StartRouter
    from handlers.start_handlers import router as start_handler

    from handlers.users.stress_test import router as stress_test_handlers
    from handlers.users.day_card import router as day_card_handlers
    from handlers.users.invite_friends import router as invite_friend_handlers
    from handlers.users.review import router as review_handlers
    from handlers.users.cabinet import router as cabinet_handlers
    from handlers.users.hint_month import router as hint_month_handlers
    from handlers.users.compatibility import router as compatibility_handlers
    from handlers.users.advice import router as advice_handlers
    from handlers.users.call_psyhologist import router as call_psyhologist_handlers

    from handlers.admin.admin_mailing_router import router as admin_mailing_router
    from handlers.admin.admin_utm import router as admin_utm_router

    dp.include_router(start_handler)
    dp.include_router(stress_test_handlers)
    dp.include_router(day_card_handlers)
    dp.include_router(invite_friend_handlers)
    dp.include_router(review_handlers)
    dp.include_router(cabinet_handlers)
    dp.include_router(hint_month_handlers)
    dp.include_router(compatibility_handlers)
    dp.include_router(advice_handlers)
    dp.include_router(call_psyhologist_handlers)

    dp.include_router(admin_mailing_router)
    dp.include_router(admin_utm_router)



    try:
        print('Bot starting...')
        await dp.start_polling(bot)
    except (KeyboardInterrupt, SystemExit):
        print('Bot stopping...')
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
