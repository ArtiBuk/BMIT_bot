from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import os
import json
import logging
from .handlers import start_handler, username_handler, password_handler, last_name_handler, first_name_handler, birthday_handler, action_handler
from .states import RegistrationState

# Установка уровня логирования
logging.basicConfig(level=logging.INFO)

# Получение логгера
logger = logging.getLogger(__name__)
# Получение абсолютного пути к файлу bot.py
current_dir = os.path.dirname(os.path.abspath(__file__))

# Формирование пути к config.json
config_path = os.path.join(current_dir, 'config.json')

# Чтение файла конфигурации
with open(config_path, 'r') as config_file:
    CONFIG = json.load(config_file)

# Получение токена бота
telegram_token = CONFIG['telegram']['token']
storage = MemoryStorage()
bot = Bot(token=telegram_token)

dp = Dispatcher(bot, storage=storage)

dp.register_message_handler(start_handler, commands=['start'])
dp.register_message_handler(action_handler, state=RegistrationState.WaitingForAction)
dp.register_message_handler(username_handler, state=RegistrationState.WaitingForUsername)
dp.register_message_handler(password_handler, state=RegistrationState.WaitingForPassword)
dp.register_message_handler(last_name_handler, state=RegistrationState.WaitingForLastName)
dp.register_message_handler(first_name_handler, state=RegistrationState.WaitingForFirstName)
dp.register_message_handler(birthday_handler, state=RegistrationState.WaitingForBirthday)





