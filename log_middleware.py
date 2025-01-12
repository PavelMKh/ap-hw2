import logging
from aiogram import BaseMiddleware
from aiogram.types import Message

from config import LOG_LEVEL

logging.basicConfig(level=LOG_LEVEL)

class LoggingMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        if isinstance(event, Message):
            logging.info(f"Получено сообщение: {event.text} от пользователя: {event.from_user.id}")
        return await handler(event, data)