
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from keyboards.inline_keyboards.ikb import IKB
from states.user_states import StressTestStates
from static.const import stress_test_advice

router = Router()

def get_advice(score):
    for (min_score, max_score), advice in stress_test_advice.items():
        if min_score <= score <= max_score:
            return advice

@router.callback_query(F.data == "stress_test")
async def stress_test(callback: CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="Начать",
            callback_data="start_stress_test"
        ),
        InlineKeyboardButton(
            text="В главное меню",
            callback_data="back_to_main_menu"
        ),
    )
    await callback.message.edit_text("""Уровень стресса — отражение твоего внутреннего состояния.
Выбери вариант ответа — тот, что ближе сейчас.
Результат теста может меняться — в зависимости от происходящего в твоей жизни.

<b>Для начала теста нажми кнопку ниже</b>""", reply_markup=builder.as_markup())

@router.callback_query(F.data == "start_stress_test")
async def stress_test_questions_1(callback: CallbackQuery, state: FSMContext):
    await state.set_state(StressTestStates.question_1)
    await callback.message.edit_text("1. Насколько часто неожиданные неприятности выводят вас из равновесия?", reply_markup=await IKB.User.stress_test_keyboard())


@router.callback_query(F.data.startswith("response_"))
async def stress_test_questions(callback: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    data = await state.get_data()
    points_data = data.get("points", 0)
    raw_points = int(callback.data.split("_")[1])

    # Определяем, нужно ли инвертировать баллы (для вопроса 5)
    if current_state == StressTestStates.question_5:
        points = 4 - raw_points  # Инвертируем баллы (0->4, 1->3, 2->2, 3->1, 4->0)
    else:
        points = raw_points

    new_points = points_data + points

    # Обновляем данные состояния
    await state.update_data(points=new_points)

    # Обрабатываем переход между вопросами
    if current_state == StressTestStates.question_1:
        await state.set_state(StressTestStates.question_2)
        await callback.message.edit_text(
            "2. Как часто вы злитесь по поводу вещей, которые вы не можете контролировать?",
            reply_markup=await IKB.User.stress_test_keyboard()
        )

    elif current_state == StressTestStates.question_2:
        await state.set_state(StressTestStates.question_3)
        await callback.message.edit_text(
            "3. Как часто вы чувствуете себя «нервозным», подавленным?",
            reply_markup=await IKB.User.stress_test_keyboard()
        )

    elif current_state == StressTestStates.question_3:
        await state.set_state(StressTestStates.question_4)
        await callback.message.edit_text(
            "4. Часто ли вы думаете, что накопилось столько трудностей, что их невозможно преодолеть?",
            reply_markup=await IKB.User.stress_test_keyboard()
        )

    elif current_state == StressTestStates.question_4:
        await state.set_state(StressTestStates.question_5)
        await callback.message.edit_text(
            "5. Как часто вы в силах контролировать раздражение?",
            reply_markup=await IKB.User.stress_test_keyboard()
        )

    elif current_state == StressTestStates.question_5:
        await state.set_state(StressTestStates.question_6)
        await callback.message.edit_text(
            "6. Насколько часто у вас возникает чувство, что вам не справиться с тем, что от вас требуется?",
            reply_markup=await IKB.User.stress_test_keyboard()
        )

    elif current_state == StressTestStates.question_6:
        await state.set_state(StressTestStates.question_7)
        await callback.message.edit_text(
            "7. Насколько часто вам кажется, что самые важные вещи в вашей жизни выходят из под вашего контроля?",
            reply_markup=await IKB.User.stress_test_keyboard()
        )

    elif current_state == StressTestStates.question_7:
        advice = get_advice(new_points)
        await callback.message.edit_text(
            advice,
            reply_markup=await IKB.User.get_main_menu()
        )
        await state.clear()