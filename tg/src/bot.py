from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import os
import json
import logging
from .handlers import (
    start_handler,
    username_handler,
    last_name_handler,
    first_name_handler,
    birthday_handler,
    action_handler,
    project_handler,
    date_handler,
    hours_handler,
    text_report_handler,
    month_handler,
    project_view_handler,
)

from .states import RegistrationState

from apscheduler.schedulers.asyncio import AsyncIOScheduler
import pytz
import datetime
import aiohttp
import asyncio

# Установка уровня логирования
logging.basicConfig(level=logging.INFO)

# Получение логгера
logger = logging.getLogger(__name__)
# Получение абсолютного пути к файлу bot.py
current_dir = os.path.dirname(os.path.abspath(__file__))

# Формирование пути к config.json
config_path = os.path.join(current_dir, "config.json")

# Чтение файла конфигурации
with open(config_path, "r") as config_file:
    CONFIG = json.load(config_file)

# Получение токена бота
telegram_token = CONFIG["telegram"]["token"]
storage = MemoryStorage()
bot = Bot(token=telegram_token)

dp = Dispatcher(bot, storage=storage)

dp.register_message_handler(start_handler, commands=["start"])
dp.register_message_handler(action_handler, state=RegistrationState.WaitingForAction)
dp.register_message_handler(
    month_handler, state=RegistrationState.WaitingForViewsReportDate
)
dp.register_message_handler(
    project_view_handler, state=RegistrationState.WaitingForViewsReportProject
)
dp.register_message_handler(project_handler, state=RegistrationState.WaitingForProject)
dp.register_message_handler(date_handler, state=RegistrationState.WaitingForDateProject)
dp.register_message_handler(
    text_report_handler, state=RegistrationState.WaitingForTextReportProject
)
dp.register_message_handler(
    hours_handler, state=RegistrationState.WaitingForHoursProject
)
dp.register_message_handler(
    username_handler, state=RegistrationState.WaitingForUsername
)
dp.register_message_handler(
    last_name_handler, state=RegistrationState.WaitingForLastName
)
dp.register_message_handler(
    first_name_handler, state=RegistrationState.WaitingForFirstName
)
dp.register_message_handler(
    birthday_handler, state=RegistrationState.WaitingForBirthday
)

KRSK_TZ = pytz.timezone("Asia/Krasnoyarsk")


async def get_json(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.json()


async def check_reports():
    today = datetime.date.today()
    formatted_today = today.strftime("%d.%m.%Y")
    users = await get_json("http://127.0.0.1:8000/api/back/users/view/")
    for user in users:
        user_id = user["id"]
        user_reports = await get_json(
            f"http://127.0.0.1:8000/api/back/reports/view/?user_id={user_id}"
        )
        if not any(report["date"] == today.isoformat() for report in user_reports):
            await bot.send_message(
                user["tg_id"],
                f"Напоминание, отчет за {formatted_today} не предоставлен",
            )


async def on_startup(dp):
    await asyncio.sleep(1)
    scheduler = AsyncIOScheduler(timezone=KRSK_TZ)
    scheduler.add_job(check_reports, "cron", hour=20)
    scheduler.add_job(check_reports, "cron", hour=23, minute=59)
    scheduler.start()
