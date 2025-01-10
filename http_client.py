import httpx

async def get_weather(city, api_key):
    async with httpx.AsyncClient() as client:
        response = await client.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric')
        
        if response.status_code == 200:
            weather_data = response.json()
            temp = weather_data['main']['temp']
            return temp
        else:
            raise Exception(f"Error fetching weather data: {response.status_code}")
        

async def get_food_calories(product_name):
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(f"https://world.openfoodfacts.org/cgi/search.pl?action=process&search_terms={product_name}&json=true")
        
        if response.status_code == 200:
            data = response.json()
            products = data.get('products', [])
            if products:
                first_product = products[0]
                return {
                    'name': first_product.get('product_name', 'Неизвестно'),
                    'calories': first_product.get('nutriments', {}).get('energy-kcal_100g', 0)
                }
            return None
        else:
            raise Exception(f"Error fetching food data: {response.status_code}")