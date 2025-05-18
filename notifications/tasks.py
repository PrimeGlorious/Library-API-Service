from celery import shared_task
from aiogram import Bot
from django.conf import settings

bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)

@shared_task
def send_telegram_message(chat_id: int, text: str):
    import asyncio
    async def send():
        await bot.send_message(chat_id=chat_id, text=text)
    asyncio.run(send())
