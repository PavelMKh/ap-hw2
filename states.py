from aiogram.fsm.state import State, StatesGroup

class Form(StatesGroup):
    weight = State()
    height = State()
    gender = State()
    age = State()
    activity = State()
    city = State()
    goal = State()
    water = State()

class Callories(StatesGroup):
    food_callories = State()
    food_weight = State()