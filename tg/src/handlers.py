from aiogram import types
from aiogram.dispatcher import FSMContext
import aiohttp
from src.states import RegistrationState
from src.keyboard import get_registration_keyboard
import json
import os
import re

async def start_handler(message: types.Message, state: FSMContext):
    await message.answer("Привет! Добро пожаловать!", reply_markup=get_registration_keyboard())
    await RegistrationState.WaitingForAction.set()

async def action_handler(message: types.Message, state: FSMContext):
    action = message.text
    if action == 'Регистрация':
        await message.answer("Введите имя пользователя:")
        await RegistrationState.WaitingForUsername.set()
    elif action == 'Отмена':
        await message.answer("Отменено.")
        await state.finish()
    else:
        await message.answer("Неверная команда. Пожалуйста, выберите действие.")
        return

async def username_handler(message: types.Message, state: FSMContext):
    username = message.text
    await state.update_data(username=username)
    await message.answer("Введите пароль:")
    await RegistrationState.WaitingForPassword.set()

async def password_handler(message: types.Message, state: FSMContext):
    password = message.text
    if not is_valid_password(password):
        await message.answer("Пароль не соответствует требованиям. Пожалуйста, введите другой пароль.")
        return
    await state.update_data(password=password)
    await message.answer("Введите фамилию:")
    await RegistrationState.WaitingForLastName.set()

async def last_name_handler(message: types.Message, state: FSMContext):
    last_name = message.text
    await state.update_data(last_name=last_name)
    await message.answer("Введите имя:")
    await RegistrationState.WaitingForFirstName.set()

async def first_name_handler(message: types.Message, state: FSMContext):
    first_name = message.text
    await state.update_data(first_name=first_name)
    await message.answer("Введите день рождения в формате YYYY-MM-DD:")
    await RegistrationState.WaitingForBirthday.set()

async def birthday_handler(message: types.Message, state: FSMContext):
    birthday = message.text
    await state.update_data(birthday=birthday)
    tg_id = message.from_user.id
    await state.update_data(tg_id=tg_id)
    user_data = await state.get_data()

    # Получение абсолютного пути к файлу config.json
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, 'config.json')

    # Чтение конфигурационного файла
    with open(config_path, 'r') as config_file:
        config = json.load(config_file)

    drf_config = config.get('drf', {})
    base_url = drf_config.get('base_url')
    create_user_endpoint = drf_config.get('create_user_endpoint')

    if not base_url or not create_user_endpoint:
        await message.answer("Произошла ошибка при регистрации. Пожалуйста, попробуйте еще раз.")
        return

    # Отправка данных регистрации на DRF API
    api_url = base_url + create_user_endpoint
    headers = {'Content-Type': 'application/json'}
    payload = {
        "username": user_data.get("username"),
        "password": user_data.get("password"),
        "first_name": user_data.get("first_name"),
        "last_name": user_data.get("last_name"),
        "birthday": user_data.get("birthday"),
        "tg_id": user_data.get("tg_id")
    }

    async with aiohttp.ClientSession(trust_env=True) as session:
        async with session.post(api_url, json=payload, headers=headers, ssl=False) as response:
            if response.status == 201:
                await message.answer("Регистрация успешно завершена!")
            else:
                await message.answer("Произошла ошибка при регистрации. Пожалуйста, попробуйте еще раз.")

    # Сброс состояния после завершения регистрации
    await state.reset_state()

def is_valid_password(password):
    # Проверка требований к паролю
    min_password_length = 8
    if len(password) < min_password_length:
        return False

    if not re.search(r"[A-Z]", password):
        return False

    if not re.search(r"[a-z]", password):
        return False

    if not re.search(r"\d", password):
        return False

    common_passwords = ["password", "123456"]  # Список часто встречающихся паролей
    if password.lower() in common_passwords:
        return False

    return True












