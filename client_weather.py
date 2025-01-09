import aiohttp

async def get_weather_async(city, api_key):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric') as response:
            if response.status == 200:
                weather_data = await response.json()
                temp = weather_data['main']['temp']
                return temp
            else:
                raise Exception(f"Error fetching weather data: {response.status}")