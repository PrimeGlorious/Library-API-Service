import asyncio
import os
import django
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from django.contrib.auth import authenticate

load_dotenv()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "telegram_drf_project.settings")
django.setup()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

auth_sessions = {}

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    auth_sessions[message.chat.id] = {"step": "username"}
    await message.answer("👤 Please enter your username:")

@dp.message(F.text)
async def handle_auth(message: types.Message):
    chat_id = message.chat.id
    session = auth_sessions.get(chat_id)

    if not session:
        await message.answer("Please type /start to begin authentication.")
        return

    # Step 1: receive username
    if session["step"] == "username":
        session["username"] = message.text.strip()
        session["step"] = "password"
        await message.answer("🔐 Now enter your password:")

    # Step 2: receive password and authenticate
    elif session["step"] == "password":
        username = session["username"]
        password = message.text.strip()
        user = authenticate(username=username, password=password)

        if user:
            user.telegram_chat_id = chat_id
            user.save()
            await message.answer("✅ Auth successful. You will now receive notifications about your books and borrowings.")
        else:
            await message.answer("❌ Invalid credentials. Type /start to try again.")

        auth_sessions.pop(chat_id, None)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
