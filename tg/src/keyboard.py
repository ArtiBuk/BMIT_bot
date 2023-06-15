from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_main_keyboard():
    registration_time_button = KeyboardButton("Регистрация времени")
    view_reports_button = KeyboardButton("Просмотр отчетов")
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(registration_time_button, view_reports_button)
    return keyboard


def get_project_buttons(projects):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    for project in projects:
        project_name = project.get("name")
        keyboard.add(KeyboardButton(project_name))
    return keyboard


