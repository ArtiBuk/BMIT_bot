from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_registration_keyboard():
    registration_button = KeyboardButton('Регистрация')
    cancel_button = KeyboardButton('Отмена')
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(registration_button, cancel_button)
    return keyboard
