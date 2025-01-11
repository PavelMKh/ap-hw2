from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder


from states import Form, Callories
from user_repository import UserRepository
from user import User
from service import calculate_caloric_goal, calculate_water_level, calculate_callories, CALORIES_PER_MINUTE, calculate_burned_callories
from http_client import get_food_calories

router = Router()
user_repository = UserRepository()

# Обработчик команды /start
@router.message(Command("start"))
async def cmd_start(message: Message):
    text = (
        "Доступные команды:\n"
        "/start - Приветствие и начало работы с ботом.\n"
        "/set_profile - Заполнить или изменить профиль.\n"
        "/show_profile - Посмотреть ваш профиль.\n"
        "/log_water <количество> - Записать количество выпитой воды в миллилитрах.\n"
        "/log_food <название продукта> - Записать количество съеденных каллорий.\n"
        "/log_workout <тип тренировки> <время (мин)> - Записать тренировку\n"
        "/check_progress - Показать прогресс"
    )
    await message.answer(text)


# Обработчик команды /set_profile
@router.message(Command("set_profile"))
async def process_height_command(message: Message, state: FSMContext):
    user_id = user_repository.create_user()
    await state.update_data(user_id=user_id)
    
    await message.answer("Введите Ваш рост (см): ")
    await state.set_state(Form.height)


@router.message(Form.height)
async def process_weight(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_id = data['user_id']
    
    try:
        height = float(message.text)
        if height <= 0:
            raise ValueError("Рост должен быть положительным числом.")
        
        user_repository.get_user(user_id).update_data(height=height)
        await message.answer("Теперь введите ваш вес (в кг):")
        await state.set_state(Form.weight)
        
    except ValueError:
        await message.answer("Ошибка: Пожалуйста, введите корректное числовое значение для роста.")


@router.message(Form.weight)
async def process_gender(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_id = data['user_id']
    
    try:
        weight = float(message.text)
        if weight <= 0:
            raise ValueError("Вес должен быть положительным числом.")
        
        user_repository.get_user(user_id).update_data(weight=weight)

        kb = [
            [types.KeyboardButton(text="М")],
            [types.KeyboardButton(text="Ж")]
        ]

        keyboard = types.ReplyKeyboardMarkup(
            keyboard=kb,
            resize_keyboard=True,
            input_field_placeholder="Выберите ваш пол"
        )

        await message.answer("Теперь выберите ваш пол:", reply_markup=keyboard)
        await state.set_state(Form.gender)
        
    except ValueError:
        await message.answer("Ошибка: Пожалуйста, введите корректное числовое значение для веса.")


@router.message(Form.gender)
async def process_age(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_id = data['user_id']
    
    gender = message.text
    user_repository.get_user(user_id).update_data(gender=gender)
    
    await message.answer("Теперь введите ваш возраст (в годах):", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(Form.age)


@router.message(Form.age)
async def process_activity(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_id = data['user_id']
    
    try:
        age = int(message.text)
        if age < 0:
            raise ValueError("Возраст не может быть отрицательным.")
        
        user_repository.get_user(user_id).update_data(age=age)
        await message.answer("Теперь введите ваш уровень активности (минут в день):")
        await state.set_state(Form.activity)
        
    except ValueError:
        await message.answer("Ошибка: Пожалуйста, введите корректное целое число для возраста.")



@router.message(Form.activity)
async def process_activity(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_id = data['user_id']
    
    try:
        activity = int(message.text)
        if activity < 0:
            raise ValueError("Уровень активности не может быть отрицательным.")
        
        user_repository.get_user(user_id).update_data(activity=activity)
        
        await message.answer("Теперь введите ваш город:")
        await state.set_state(Form.city)
        
    except ValueError:
        await message.answer("Ошибка: Пожалуйста, введите корректное целое число для уровня активности.")


@router.message(Form.city)
async def process_goal(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_id = data['user_id']
    city = message.text

    user = user_repository.get_user(user_id)
    user.update_data(city=city)

    caloric_goal = calculate_caloric_goal(user)
    water_goal = await calculate_water_level(user)

    user.update_data(calorie_goal=caloric_goal, water_goal=water_goal)

    kb = [
        [types.KeyboardButton(text="Да")],
        [types.KeyboardButton(text="Изменить")]
    ]

    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Сохранить цель по калориям"
    )

    await message.answer(
        f"Ваша цель по калориям: {caloric_goal:.2f} ккал. "
        f"Ваша цель по воде: {water_goal:.2f} мл. "
        "Если вы хотите изменить это значение, нажмите 'Изменить' или 'Да', чтобы подтвердить.",
        reply_markup=keyboard
    )
    
    await state.set_state(Form.goal)


@router.message(Form.goal)
async def confirm_goal(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_id = data['user_id']
    user_input = message.text
    
    user = user_repository.get_user(user_id)
    
    if user_input == "Да":
        water_level = await calculate_water_level(user)
        user.update_data(water_goal=water_level)
        
        await message.answer("Цель подтверждена. Спасибо!", reply_markup=types.ReplyKeyboardRemove())
        await cmd_start(message)  
        await state.clear()
        
    elif user_input == "Изменить":
        await message.answer("Введите новое значение для цели по калориям:", reply_markup=types.ReplyKeyboardRemove())
        await state.set_state(Form.goal)  
        
    else:
        try:
            new_goal = float(user_input)
            user.update_data(calorie_goal=new_goal)
            
            water_level = await calculate_water_level(user)
            user.update_data(water_goal=water_level)
            
            await message.answer(f"Ваша новая цель по калориям установлена: {new_goal:.2f} ккал.")
            await cmd_start(message)  
            await state.clear()  
            
        except ValueError:
            await message.reply("Пожалуйста, введите корректное значение или выберите одну из кнопок.")


# Обработчик команды /show_profile
@router.message(Command("show_profile"))
async def process_show_profile(message: Message, state: FSMContext):
    user = user_repository.get_current_user()

    if user is None:
        await message.answer("Ошибка: Не удалось найти текущего пользователя.")
        return

    profile_message = (
        f"Ваш профиль:\n"
        f"Вес: {user.weight} кг\n"
        f"Рост: {user.height} см\n"
        f"Пол: {user.gender}\n"
        f"Возраст: {user.age} лет\n"
        f"Уровень активности: {user.activity} минут в день\n"
        f"Город: {user.city}\n"
        f"Цель по калориям: {user.calorie_goal} ккал\n"
        f"Цель по выпитой воде: {user.water_goal} мл\n"
        f"Выпито воды: {user.get_total_water()} мл\n"
        f"Съедено каллорий: {user.get_total_calories()} ккал"
    )

    await message.answer(profile_message, reply_markup=types.ReplyKeyboardRemove())


# Обработчик команды log_water
@router.message(Command("log_water"))
async def log_water(message: Message, state: FSMContext):
    user = user_repository.get_current_user()

    if user is None:
        await message.answer("Ошибка: Не удалось найти текущего пользователя.")
        return
    
    command_text = message.text.split()
    
    if len(command_text) != 2:
        await message.answer("Пожалуйста, укажите количество воды в миллилитрах после команды. Например: /log_water 250")
        return
    
    try:
        amount = float(command_text[1])
        user.log_water(amount)
        total_water = user.get_total_water()
        water_goal = user.water_goal - total_water
        if water_goal > 0:
            await message.answer(f"За сегодня выпито воды: {total_water:.2f} мл. До достижения цели нужно выпить {water_goal:.2f} мл.")
        else:
            await message.answer(f"За сегодня выпито воды: {total_water:.2f} мл. Цель достигнута.")
            
    except ValueError:
         await message.answer("Пожалуйста, введите корректное число.")


# Обработчик команды /log_food
@router.message(Command("log_food"))
async def log_food(message: Message, state: FSMContext):
    command_text = message.text.split()

    if len(command_text) != 2:
        await message.answer("Пожалуйста, укажите название продукта. Например: /log_food чебурек")
        return
    
    food_name = command_text[1]

    food_data = await get_food_calories(food_name)

    if food_data is None:
        await message.answer(f"Для продукта '{food_name}' данных нет.")
        await state.clear()
        return

    callories = food_data['calories']
    
    await state.update_data(food_callories=callories)

    await message.answer(f"{food_name} - {callories} ккал на 100 г. Сколько грамм вы съели?")
    await state.set_state(Callories.food_callories)


@router.message(Callories.food_callories)
async def process_callories(message: types.Message, state: FSMContext):
    try:
        weight = float(message.text) 
        await state.update_data(food_weight=weight) 
        await state.set_state(Callories.food_weight)
        
    except ValueError:
        await message.answer("Ошибка: Пожалуйста, введите корректное числовое значение для веса еды.")
        return

    if weight < 0:
        await message.answer("Ошибка: Вес еды не может быть отрицательным.")
        return

    data = await state.get_data()
    food_weight = data.get('food_weight')
    food_callories = data.get('food_callories')

    if food_weight is None or food_callories is None:
        await message.answer("Ошибка: Не удалось получить данные о калориях или весе.")
        return

    total_cal = calculate_callories(food_callories, food_weight)

    user = user_repository.get_current_user()
    user.log_food(total_cal)
    await message.answer(f"Записано: {total_cal} ккал")
    await cmd_start(message)  
    await state.clear()

# Обработчик команды /log_workout
@router.message(Command("log_workout"))
async def log_workout(message: types.Message):
    args = message.text.split()

    user = user_repository.get_current_user()
    
    if len(args) != 3:
        await message.answer("Пожалуйста, используйте формат: /log_workout <тип тренировки> <длительность в минутах>")
        return

    workout_type = args[1].lower()
    duration_minutes = int(args[2])

    if workout_type not in CALORIES_PER_MINUTE:
        await message.answer("Неизвестный тип тренировки. Пожалуйста, используйте один из следующих: " + ", ".join(CALORIES_PER_MINUTE.keys()))
        return

    calories_burned = calculate_burned_callories(workout_type, duration_minutes)
    add_water = duration_minutes * 500 / 30

    user.log_workout(calories_burned)
    user.add_water(add_water)

    await message.answer(
        f"{workout_type.capitalize()} {duration_minutes} минут — {calories_burned} ккал.\n"
        f"Дополнительно: выпейте {round(add_water)} мл воды."
        )
    

# Обработчик команды /check_progress
@router.message(Command("check_progress"))
async def show_progress(message: types.Message):
    user = user_repository.get_current_user()

    progress_message = (
        f"📊 Прогресс:\n"
        f"Вода:\n"
        f"- Выпито: {user.logged_water} мл из {user.water_goal} мл.\n"
        f"- Осталось: {user.water_goal - user.logged_water} мл.\n"
        f"\nКалории:\n"
        f"- Потреблено: {user.logged_calories} ккал из {user.calorie_goal} ккал."
        f"- Сожжено: {user.burned_calories} ккал.\n"
        f"- Баланс: {user.calorie_goal - user.logged_calories + user.burned_calories} ккал.\n"
    )

    await message.answer(progress_message)
