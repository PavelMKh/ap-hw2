from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder


from states import Form
from water_tracker import InMemoryWaterTracker

router = Router()
in_memory_water_tracker = InMemoryWaterTracker()

# Обработчик команды /start
@router.message(Command("start"))
async def cmd_start(message: Message):
    text = (
        "Доступные команды:\n"
        "/start - Приветствие и начало работы с ботом.\n"
        "/log_water <количество> - Записать количество выпитой воды в миллилитрах.\n"
        "/show_profile - Посмотреть ваш профиль.\n"
        "/set_profile - Заполнить или изменить профиль.\n"
        "Если у вас есть вопросы, просто напишите мне!"
    )
    await message.answer(text)


# Вызываем то же самое, только через команду
@router.message(Command("set_profile"))
async def process_height_command(message: Message, state: FSMContext):
    await message.answer("Введите Ваш рост (см): ")
    await state.set_state(Form.height)


@router.message(Form.height)
async def process_weight(message: types.Message, state: FSMContext):
    try:
        height = float(message.text)
        if height < 0:
            raise ValueError("Рост не может быть отрицательным.")
        
        await state.update_data(height=height)
        await message.answer("Теперь введите ваш вес (в кг):")
        await state.set_state(Form.weight)
    except ValueError:
        await message.answer("Ошибка: Пожалуйста, введите корректное числовое значение для роста.")

@router.message(Form.weight)
async def process_gender(message: types.Message, state: FSMContext):
    try:
        weight = float(message.text)
        if weight < 0:
            raise ValueError("Вес не может быть отрицательным.")
        
        await state.update_data(weight=weight)

        kb = [
            [types.KeyboardButton(text="М")],
            [types.KeyboardButton(text="Ж")]
        ]

        keyboard = types.ReplyKeyboardMarkup(
            keyboard=kb,
            resize_keyboard=True,
            input_field_placeholder="Выберите ваш пол")

        await message.answer("Теперь выберите ваш пол:", reply_markup=keyboard)
        await state.set_state(Form.gender)
    except ValueError:
        await message.answer("Ошибка: Пожалуйста, введите корректное числовое значение для веса.")

@router.message(Form.gender)
async def process_age(message: types.Message, state: FSMContext):
    gender = message.text
    await state.update_data(gender=gender)
    await message.answer("Теперь введите ваш возраст (в годах):", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(Form.age)


@router.message(Form.age)
async def process_activity(message: types.Message, state: FSMContext):
    try:
        age = int(message.text)
        if age < 0:
            raise ValueError("Возраст не может быть отрицательным.")
        
        await state.update_data(age=age)
        await message.answer("Теперь введите ваш уровень активности (минут в день):")
        await state.set_state(Form.activity)
    except ValueError:
        await message.answer("Ошибка: Пожалуйста, введите корректное целое число для возраста.")


@router.message(Form.activity)
async def process_city(message: types.Message, state: FSMContext):
    activity = int(message.text)
    await state.update_data(activity=activity)
    await message.answer("Теперь введите ваш город:")
    await state.set_state(Form.city)


@router.message(Form.city)
async def process_goal(message: types.Message, state: FSMContext):
    city = message.text
    await state.update_data(city=city)
    user_data = await state.get_data()
    caloric_goal = calculate_caloric_goal(user_data)
    await state.update_data(goal=caloric_goal)

    kb = [
        [types.KeyboardButton(text="Да")],
        [types.KeyboardButton(text="Изменить")]
    ]

    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Сохранить цель по каллориям")

    await message.answer(
        f"Ваша цель по калориям: {caloric_goal:.2f} ккал. "
        "Если вы хотите изменить это значение, нажмите 'Изменить' или 'Да', чтобы подтвердить.",
        reply_markup=keyboard
    )
    await state.set_state(Form.goal)

@router.message(Form.goal)
async def confirm_goal(message: types.Message, state: FSMContext):
    user_input = message.text
    user_data = await state.get_data()

    if user_input == "Да":
        water_level = calculate_water_level(user_data)
        await state.update_data(water=water_level)
        await message.answer("Цель подтверждена. Спасибо!", reply_markup=types.ReplyKeyboardRemove())
        await cmd_start(message)
        await state.set_state(None)
    elif user_input == "Изменить":
        await message.answer("Введите новое значение для цели по калориям:", reply_markup=types.ReplyKeyboardRemove())
        await state.set_state(Form.goal)
    elif user_input.isdigit():
        new_goal = float(user_input)
        await state.update_data(goal=new_goal)
        water_level = calculate_water_level(user_data)
        await state.update_data(water=water_level)
        await message.answer(f"Ваша новая цель по калориям установлена: {new_goal:.2f} ккал.")
        await cmd_start(message)
        await state.set_state(None)
    else:
        await message.reply("Пожалуйста, введите корректное значение или выберите одну из кнопок.")


def calculate_bmr(weight, height, age, gender):
    """Расчет базового уровня метаболизма (BMR)"""
    if gender == 'М':
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    return bmr


def calculate_caloric_goal(user_data):
    """Расчет цели по калориям на основе BMR и уровня активности"""
    bmr = calculate_bmr(user_data['weight'], user_data['height'], user_data['age'], user_data['gender'])
    caloric_goal = bmr + (user_data['activity'] / 60) * 200
    return round(caloric_goal)


def calculate_water_level(user_data):
    """Расчет цели по потреблению воды"""
    return user_data['weight'] * 30


# Обработчик команды /show_profile
@router.message(Command("show_profile"))
async def process_show_profile(message: Message, state: FSMContext):
    user_data = await state.get_data()

    profile_message = (
        f"Ваш профиль:\n"
        f"Вес: {user_data.get('weight', 'Не установлен')} кг\n"
        f"Рост: {user_data.get('height', 'Не установлен')} см\n"
        f"Пол: {user_data.get('gender', 'Не установлен')}\n"
        f"Возраст: {user_data.get('age', 'Не установлен')} лет\n"
        f"Уровень активности: {user_data.get('activity', 'Не установлен')} минут в день\n"
        f"Город: {user_data.get('city', 'Не установлен')}\n"
        f"Цель по калориям: {user_data.get('goal', 'Не установлена')} ккал\n"
        f"Цель по выпитой воде: {user_data.get('water')} мл\n"
        f"Выпито воды: {in_memory_water_tracker.get_total_water()} мл"
    )

    await message.answer(profile_message, reply_markup=types.ReplyKeyboardRemove())


@router.message(Command("log_water"))
async def log_water(message: Message, state: FSMContext):
    command_text = message.text.split()
    user_data = await state.get_data()
    
    if len(command_text) != 2:
        await message.answer("Пожалуйста, укажите количество воды в миллилитрах после команды. Например: /log_water 250")
        return
    
    try:
        amount = float(command_text[1])
        if amount < 0:
            raise ValueError("Количество не может быть отрицательным.")
        
        in_memory_water_tracker.log_water(amount)
        water_goal = float(user_data.get('water')) - in_memory_water_tracker.get_total_water()
        if water_goal > 0:
            await message.answer(f"За сегодня выпито воды: {in_memory_water_tracker.get_total_water()} мл. До достижения цели нужно выпить {water_goal} мл.")
        else:
            await message.answer(f"За сегодня выпито воды: {in_memory_water_tracker.get_total_water()} мл. Цель {user_data.get('water')} мл достигнута.")
    except ValueError:
        await message.answer(f"Пожалуйста, введите корректное число.")