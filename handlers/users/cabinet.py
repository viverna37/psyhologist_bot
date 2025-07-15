from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from config import Config
from database.db import DataBase
from database.models import UserSubscription, Referral, UserBalance
from keyboards.inline_keyboards.ikb import IKB
from states.user_states import BuySubscriptionStates

router = Router()


def calculate_payment(subscription_price: int, user_balance: int) -> dict:
    """
    Рассчитывает списание баллов и итоговую сумму к оплате.

    Возвращает словарь с:
    - points_deduction: сколько баллов спишется
    - final_price: итоговая сумма к оплате
    - saved: сколько сэкономили баллами
    """
    max_deduction = int(subscription_price * 0.3)
    points_deduction = min(user_balance, max_deduction)

    return {
        "points_deduction": points_deduction,
        "final_price": subscription_price - points_deduction
    }

@router.callback_query(F.data == "cabinet")
async def cabinet(callback: CallbackQuery, db: DataBase):
    sub_data = await db.get_from_db(UserSubscription, filters={"user_id": callback.from_user.id})
    user_balance = await db.get_from_db(UserBalance, filters={"user_id": callback.from_user.id})
    user_balance = user_balance[0].balance
    reff_data = await db.get_from_db(Referral, filters={"referrer_id": callback.from_user.id})
    await callback.message.edit_text(f"""Ваш личный кабинет
    
<b>📅 Подписка активна до:</b> {sub_data[0].date_ended if sub_data and sub_data[0].is_active else 'Нет'}
<b>💎 Формат:</b> {"✨ Улучшенный" if sub_data and sub_data[0].type_subscription == 1 else "👑 Премиум" if sub_data and sub_data[0].type_subscription == 2 else '📦 Стандарт'}
<b>👥 Приглашённые друзья:</b> {len(reff_data)}
<b>💰 Баланс:</b> {user_balance} ₽""", reply_markup = await IKB.User.cabinet_keyboard())

@router.callback_query(F.data == "buy_subscription")
async def cabinet(callback: CallbackQuery, db: DataBase, state=FSMContext):
    user_balance = await db.get_from_db(UserBalance, filters={"user_id": callback.from_user.id})
    user_balance = user_balance[0].balance
    sub_data = await db.get_from_db(UserSubscription, filters={"user_id": callback.from_user.id})
    if sub_data and sub_data[0].type_subscription == 2:
        await callback.answer("У вас уже приобретена подписка, приходите после окончания", show_alert=True)
        return
    await callback.message.edit_text(f"""Выберите ваш формат подписки:

📦 <b>Стандарт</b> — для регулярной поддержки
• Подсказка на день (карта дня)
• Тест на уровень стресса
• До 3 подсказок в ситуациях каждый день
💰 <i>Доступен бесплатно</i>

✨ <b>Улучшенный</b> — для тех, кто хочет подробнее
• Всё из «стандарта»
• Ежемесячный разбор с учётом вашей даты рождения
• Безлимитные подсказки в ситуациях
✅ Максимум пользы в вашем ритме
💰 <i>Доступен по подписке {calculate_payment(299, user_balance).get("final_price")} ₽ раз в месяц</i>

👑 <b>Премиум</b> — для личных решений
• Всё из формата «Улучшенный»
• Безлимитный расчёт совместимости по числу рождения — с партнёром, друзьями, коллегами, близкими
• Вы увидите, через что строится контакт, что сближает, на чём держится доверие
✅ Для тех, кому важна ясность: что это за связь, зачем она, и как её развивать
💰 <i>Доступен по подписке {calculate_payment(399, user_balance).get("final_price")} ₽ раз в месяц</i>

🔄 Для активации подписки выполните перевод на карту Сбербанк 
2202200112216658
Имя: <i>Елизавета Сергеевна К.</i>
📩 После оплаты пришлите скриншот перевода сюда
После подтверждения подписка будет активирована автоматически.""", reply_markup = await IKB.User.back_to_main_menu_keyboard())
    await state.set_state(BuySubscriptionStates.waiting)
    await state.update_data(price=[calculate_payment(299, user_balance).get("final_price"), calculate_payment(399, user_balance).get("final_price")], points = [calculate_payment(299, user_balance).get("points_deduction"), calculate_payment(399, user_balance).get("points_deduction")])

@router.message(F.photo, StateFilter(BuySubscriptionStates.waiting))
async def cabinet(message: Message, db: DataBase, state: FSMContext, config: Config):
    data = await state.get_data()
    await message.answer("Спасибо, я получил твой скриншот. Отправил админу на проверку", reply_markup = await IKB.User.get_main_menu())
    await message.bot.send_photo(config.tg_bot.order_channel, photo=message.photo[-1].file_id, caption=f"Новый платеж\nПосле списания баллов цены были\n{data.get('price')}", reply_markup=await IKB.Admin.check_payment(message.from_user.id, data.get("points")))
    await state.clear()
