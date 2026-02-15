# ==== Dependencias ====
import asyncio
from telegram.ext import ApplicationBuilder, CommandHandler

# ==== Depencias Locales ====
from .config import TELEGRAM_TOKEN
from .api_client import get_event, get_status
from .telegram_client import send_message
from .formatter import format_event, format_status
from .scheduler import start_scheduler

# ==== Funciones ====

async def event_loop():
    while True:
        event = get_event()
        if event:
            msg = format_event(event)
            if msg:
                await send_message(msg)

        await asyncio.sleep(10)

async def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("status", status_command))

    start_scheduler()
    asyncio.create_task(event_loop())

    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
