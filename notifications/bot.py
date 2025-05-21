import asyncio
import os
import django
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from django.contrib.auth import authenticate
from asgiref.sync import sync_to_async

load_dotenv()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

auth_sessions = {}


@dp.message(Command("start"))
async def start_handler(message: types.Message):
    auth_sessions[message.chat.id] = {"step": "email"}
    await message.answer("👤 Please enter your email:")


@dp.message(F.text)
async def handle_auth(message: types.Message):
    chat_id = message.chat.id
    session = auth_sessions.get(chat_id)

    if not session:
        await message.answer("Please type /start to begin authentication.")
        return

    # Step 1: receive username
    if session["step"] == "email":
        session["email"] = message.text.strip()
        session["step"] = "password"
        await message.answer("🔐 Now enter your password:")

    # Step 2: receive password and authenticate
    elif session["step"] == "password":
        email = session["email"]
        password = message.text.strip()

        # Wrap authenticate with sync_to_async
        user = await sync_to_async(authenticate)(username=email, password=password)

        if user:
            user.chat_id = chat_id
            await sync_to_async(user.save)()
            if not user.is_staff:
                await message.answer(
                    "✅ Auth successful. You will now receive notifications about your books and borrowings."
                )
            else:
                await message.answer(
                    "✅ Auth successful. Since you are admin, you will receive notifications about all "
                    " books and borrowings changes in database🗣️."
                )
        else:
            await message.answer("❌ Invalid credentials. Type /start to try again.")

        auth_sessions.pop(chat_id, None)


async def main():
    await dp.start_polling(bot)
