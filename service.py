from user import User
from http_client import get_weather
from config import WEATHER_TOKEN

def calculate_bmr(user: User) -> float:
    """Расчет базового уровня метаболизма (BMR)"""
    weight = user.weight
    height = user.height
    age = user.age
    gender = user.gender

    if gender == 'М':
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161

    return bmr


def calculate_caloric_goal(user: User) -> float:
    """Расчет цели по калориям на основе BMR и уровня активности"""
    bmr = calculate_bmr(user)
    caloric_goal = bmr + (user.activity / 60) * 200  
    return round(caloric_goal)


def calculate_callories(callories: float, weight: float):
    """Расчет количества потребленных каллорий"""
    return callories * weight / 100


async def calculate_water_level(user: User) -> float:
    """Расчет цели по потреблению воды"""
    water_level = user.weight * 30
    temp = await get_weather(user.city, WEATHER_TOKEN)

    if temp > 25:
        water_level += 500

    return water_level