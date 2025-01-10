import os
from dotenv import load_dotenv
import logging

load_dotenv()

BOT_TOKEN = os.getenv("TG_TOKEN")
LOG_LEVEL = logging.INFO
WEATHER_TOKEN = os.getenv("WEATH_TOKEN")