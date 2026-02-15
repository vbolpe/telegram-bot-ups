from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
from .api_client import get_status
from .telegram_client import send_message
from .formatter import format_status
from .config import REPORT_HOUR

def start_scheduler():
    scheduler = AsyncIOScheduler()

    scheduler.add_job(
        daily_report,
        trigger="cron",
        hour=REPORT_HOUR,
        minute=0,
    )

    scheduler.start()

async def daily_report():
    status = get_status()
    message = " Reporte Diario UPS\n\n" + format_status(status)
    await send_message(message)