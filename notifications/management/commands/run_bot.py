import asyncio
from django.core.management.base import BaseCommand
from notifications.bot import main  # your bot's main async function

class Command(BaseCommand):
    help = "Starts the Telegram bot"

    def handle(self, *args, **options):
        asyncio.run(main())
