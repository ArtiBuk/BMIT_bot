from aiogram import types
from aiogram.dispatcher import FSMContext
import aiohttp
import json
import os
import re
import datetime
from src.states import RegistrationState
from src.keyboard import get_main_keyboard, get_project_buttons, get_month_buttons,get_back_button,add_back_button
from src.checks import check_existing_user,is_back,is_valid_date,is_valid_hours,is_valid_username


async def start_handler(message: types.Message, state: FSMContext):
    tg_id = message.from_user.id
    (
        existing_username,
        existing_projects,
        existing_user_id,
        existing_project_ids,
        active_project_id
    ) = await check_existing_user(tg_id)

    if existing_username:
        await message.answer(
            f"Привет, {existing_username}!", reply_markup=get_main_keyboard()
        )
        await RegistrationState.WaitingForAction.set()
    else:
        await message.answer(
            "Сейчас начнется регистрация. Введите ваше имя пользователя:"
        )
        await RegistrationState.WaitingForUsername.set()

    await state.update_data(
        tg_id=tg_id,
        projects=existing_projects,
        user_id=existing_user_id,
        project_ids=existing_project_ids,
        active_project_id=active_project_id
    )

async def action_handler(message: types.Message, state: FSMContext):
    action = message.text.lower()
    if action == "регистрация времени":
        data = await state.get_data()
        existing_projects = data.get("projects")
        keyboard = get_project_buttons(existing_projects)
        keyboard_with_back = add_back_button(keyboard)
        if existing_projects:
            await message.answer(
                "Выберите проект:", reply_markup=keyboard_with_back
            )
            await RegistrationState.WaitingForProject.set()
        else:
            await message.answer("У вас нет доступных проектов.")
            await state.finish()
    elif action == "просмотр отчетов":
        keyboard = get_month_buttons()
        keyboard_with_back = add_back_button(keyboard)
        await message.answer("Выберете месяц", reply_markup=keyboard_with_back)
        await RegistrationState.WaitingForViewsReportDate.set()
    else:
        await message.answer(
            "Некорректное действие. Пожалуйста, выберите 'Регистрация времени' или 'Просмотр отчетов'."
        )


async def month_handler(message: types.Message, state: FSMContext):
        data = await state.get_data()
        existing_projects = data.get("projects")
        month_name = message.text.lower()
        if is_back(month_name):
            await message.answer(
                "Выберете еще раз",reply_markup=get_main_keyboard()
            )
            await RegistrationState.WaitingForAction.set()
        else:
            month_mapping = {
                "январь": 1,
                "февраль": 2,
                "март": 3,
                "апрель": 4,
                "май": 5,
                "июнь": 6,
                "июль": 7,
                "август": 8,
                "сентябрь": 9,
                "октябрь": 10,
                "ноябрь": 11,
                "декабрь": 12,
            }

            if month_name in month_mapping:
                month_number = month_mapping[month_name]
                current_year = datetime.datetime.now().year
                month = f"{current_year}-{month_number:02d}"

                await state.update_data(month=month)
                keyboard = get_project_buttons(existing_projects)
                keyboard_with_back = add_back_button(keyboard)
                await message.answer(
                    "Выберите проект:", reply_markup=keyboard_with_back
                )
                await RegistrationState.WaitingForViewsReportProject.set()
            else:
                await message.answer(
                    "Некорректный месяц. Пожалуйста, выберите месяц из предложенных."
                )


async def project_view_handler(message: types.Message, state: FSMContext):
    project = message.text
    if is_back(project):
        keyboard = get_month_buttons()
        keyboard_with_back = add_back_button(keyboard)
        await message.answer("Выберете месяц", reply_markup=keyboard_with_back)
        await RegistrationState.WaitingForViewsReportDate.set()
    else:
        await state.update_data(project=project)

        # Получение данных из состояния
        data = await state.get_data()
        projects = data.get("projects")
        month = data.get("month")

        # Поиск выбранного проекта по имени
        selected_project = next((p for p in projects if p.get("name") == project), None)

        if selected_project:
            project_id = selected_project.get("id")
            await state.update_data(project_id=project_id)

            # Получение информации о пользователе из состояния
            user_id = data.get("user_id")

            # Получение URL и параметров запроса из файла конфигурации
            current_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(current_dir, "config.json")

            # Чтение конфигурационного файла
            with open(config_path, "r") as config_file:
                config = json.load(config_file)

            base_url = config.get("drf", {}).get("base_url")
            view_report_endpoint = config.get("drf", {}).get("view_report")

            if not base_url or not view_report_endpoint:
                await message.answer("Ошибка конфигурации сервера.")
                await state.finish()
                return

            # Составление URL для запроса
            url = f"{base_url}{view_report_endpoint}?user_id={user_id}"

            # Отправка GET-запроса для получения данных
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        try:
                            reports = await response.json()

                            # Фильтрация данных по месяцу и проекту
                            filtered_reports = [
                                r
                                for r in reports
                                if r.get("date").startswith(month)
                                and r.get("project") == project_id
                            ]

                            # Отправка пользователю отфильтрованных данных
                            if filtered_reports:
                                for report in filtered_reports:
                                    date = report.get("date")
                                    hours = report.get("hours")
                                    text_report = report.get("text_report")

                                    message_text = (
                                        f"Дата: {date}\nЧасы: {hours}\nОтчет: {text_report}"
                                    )
                                    await message.answer(message_text)
                            else:
                                await message.answer(
                                    "Нет доступных данных за выбранный месяц и проект."
                                )
                        except json.JSONDecodeError:
                            await message.answer("Ошибка при обработке данных.")
                    else:
                        await message.answer("Ошибка при выполнении запроса.")
        else:
            await message.answer(
                "Некорректный проект. Пожалуйста, выберите проект из предложенных."
            )

        await state.finish()


async def project_handler(message: types.Message, state: FSMContext):
    project = message.text
    if is_back(project):
        await message.answer(
            "Выберете еще раз",reply_markup=get_main_keyboard()
        )
        await RegistrationState.WaitingForAction.set()
    else:
        await state.update_data(project=project)

        # Получение данных из состояния
        data = await state.get_data()
        projects = data.get("projects")

        # Поиск выбранного проекта по имени
        selected_project = next((p for p in projects if p.get("name") == project), None)

        if selected_project:
            keyboard = get_back_button()
            project_id = selected_project.get("id")
            await state.update_data(project_id=project_id)
            await message.answer(
                f"Выбран проект: {project}. Введите дату в формате DD-MM-YYYY",reply_markup=keyboard
            )
            await RegistrationState.WaitingForDateProject.set()
        else:
            await message.answer(
                "Некорректный проект. Пожалуйста, выберите проект из предложенных."
            )
            # Возвращаемся к выбору проекта
            await RegistrationState.WaitingForProject.set()


async def date_handler(message: types.Message, state: FSMContext):
    date_str = message.text
    if is_back(date_str):
        data = await state.get_data()
        data = await state.get_data()
        existing_projects = data.get("projects")
        keyboard = get_project_buttons(existing_projects)
        keyboard_with_back = add_back_button(keyboard)
        if existing_projects:
            await message.answer(
                "Выберите проект:", reply_markup=keyboard_with_back
            )
            await RegistrationState.WaitingForProject.set()
    else:
        try:
            # Преобразование даты из формата "dd-mm-yyyy" в формат "yyyy-mm-dd"
            date = datetime.datetime.strptime(date_str, "%d-%m-%Y").strftime("%Y-%m-%d")
        except ValueError:
            await message.answer(
                "Некорректный формат даты. Пожалуйста, используйте формат DD-MM-YYYY."
            )
            return

        await state.update_data(date=date)
        await message.answer("Введите текст отчета:")
        await RegistrationState.WaitingForTextReportProject.set()


async def text_report_handler(message: types.Message, state: FSMContext):
    text_report = message.text
    if is_back(text_report):
        await message.answer(
                "Измените дату, используйте формат DD-MM-YYYY."
            )
        await RegistrationState.WaitingForDateProject.set()
    else:
        await state.update_data(text_report=text_report)
        await message.answer("Введите сколько часов потрачено:")
        await RegistrationState.WaitingForHoursProject.set()


async def hours_handler(message: types.Message, state: FSMContext):
    hours = message.text
    if is_back(hours):
        await message.answer(
                "Измените текст отчета"
            )
        await RegistrationState.WaitingForTextReportProject.set()
    else:
        if not is_valid_hours(hours):
            await message.answer(
                "Некорректное количество часов. Пожалуйста, введите число от 1 до 99."
            )
            return

        await state.update_data(hours=hours)

        # Получение данных из состояния
        data = await state.get_data()
        user_id = data.get("user_id")
        project_id = data.get("project_id")
        date = data.get("date")
        text_report = data.get("text_report")
        hours = data.get("hours")

        # Формирование тела POST-запроса
        payload = {
            "date": date,
            "hours": hours,
            "user": user_id,
            "project": project_id,
            "text_report": text_report,
        }

        # Получение абсолютного пути к файлу config.json
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(current_dir, "config.json")

        # Чтение конфигурационного файла
        with open(config_path, "r") as config_file:
            config = json.load(config_file)

        drf_config = config.get("drf", {})
        base_url = drf_config.get("base_url")
        create_report_endpoint = drf_config.get("create_report")

        if not base_url or not create_report_endpoint:
            await message.answer(
                "Произошла ошибка при отправке отчета. Пожалуйста, попробуйте еще раз."
            )
            return

        # Отправка данных отчета на DRF API
        api_url = base_url + create_report_endpoint
        headers = {"Content-Type": "application/json"}

        async with aiohttp.ClientSession(trust_env=True) as session:
            async with session.post(
                api_url, json=payload, headers=headers, ssl=False
            ) as response:
                if response.status == 201:
                    await message.answer("Отчет успешно создан!")
                else:
                    await message.answer(
                        "Произошла ошибка при отправке отчета. Пожалуйста, попробуйте еще раз."
                    )

        # Сброс состояния после завершения регистрации
        await state.finish()


async def username_handler(message: types.Message, state: FSMContext):
    username = message.text
    is_valid = await is_valid_username(username)
    if is_valid:
        keyboard = add_back_button()
        await state.update_data(username=username)
        await message.answer("Введите фамилию:",reply_markup=keyboard)
        await RegistrationState.WaitingForLastName.set()
    else:
        await message.answer(
            "Некорректное имя пользователя. Пожалуйста, введите другое имя пользователя:"
        )


async def last_name_handler(message: types.Message, state: FSMContext):
    last_name = message.text
    if is_back(last_name):
        keyboard = add_back_button()
        await message.answer(
            "Измените ваше имя пользователя:",reply_markup=keyboard
        )
        await RegistrationState.WaitingForUsername.set()
    else:
        await state.update_data(last_name=last_name)
        await message.answer("Введите имя:")
        await RegistrationState.WaitingForFirstName.set()


async def first_name_handler(message: types.Message, state: FSMContext):
    first_name = message.text
    if is_back(first_name):
        keyboard = add_back_button()
        await message.answer(
            "Измените фамилию:",reply_markup=keyboard
        )
        await RegistrationState.WaitingForLastName.set()
    else:
        await state.update_data(first_name=first_name)
        await message.answer("Введите день рождения в формате YYYY-MM-DD:")
        await RegistrationState.WaitingForBirthday.set()


async def birthday_handler(message: types.Message, state: FSMContext):
    birthday = message.text
    if is_back(birthday):
        keyboard = add_back_button()
        await message.answer(
            "Измените имя:",reply_markup=keyboard
        )
        await RegistrationState.WaitingForFirstName.set()
    else:
        if not is_valid_date(birthday):
            await message.answer(
                "Некорректный формат даты. Пожалуйста, используйте формат YYYY-MM-DD."
            )
            return
        await state.update_data(birthday=birthday)
        user_data = await state.get_data()

        # Получение абсолютного пути к файлу config.json
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(current_dir, "config.json")

        # Чтение конфигурационного файла
        with open(config_path, "r") as config_file:
            config = json.load(config_file)

        drf_config = config.get("drf", {})
        base_url = drf_config.get("base_url")
        create_user_endpoint = drf_config.get("create_user_endpoint")

        if not base_url or not create_user_endpoint:
            await message.answer(
                "Произошла ошибка при регистрации. Пожалуйста, попробуйте еще раз."
            )
            return

        # Отправка данных регистрации на DRF API
        api_url = base_url + create_user_endpoint
        headers = {"Content-Type": "application/json"}
        payload = {
            "username": user_data.get("username"),
            "first_name": user_data.get("first_name"),
            "last_name": user_data.get("last_name"),
            "birthday": user_data.get("birthday"),
            "tg_id": user_data.get("tg_id"),
        }

        async with aiohttp.ClientSession(trust_env=True) as session:
            async with session.post(
                api_url, json=payload, headers=headers, ssl=False
            ) as response:
                if response.status == 201:
                    await message.answer("Регистрация успешно завершена!")
                else:
                    await message.answer(
                        "Произошла ошибка при регистрации. Пожалуйста, попробуйте еще раз."
                    )

        # Сброс состояния после завершения регистрации
        await state.finish()

# async def check_existing_user(tg_id):
#     # Получение абсолютного пути к файлу config.json
#     current_dir = os.path.dirname(os.path.abspath(__file__))
#     config_path = os.path.join(current_dir, "config.json")

#     # Чтение конфигурационного файла
#     with open(config_path, "r") as config_file:
#         config = json.load(config_file)

#     drf_config = config.get("drf", {})
#     base_url = drf_config.get("base_url")
#     users_view = drf_config.get("users_view")
#     view_projects = drf_config.get("view_projects")

#     if not base_url or not users_view or not view_projects:
#         return None, None, None, None, None

#     # Отправка GET-запроса для получения списка пользователей
#     api_url_users = base_url + users_view

#     async with aiohttp.ClientSession(trust_env=True) as session:
#         async with session.get(api_url_users, ssl=False) as response:
#             if response.status == 200:
#                 try:
#                     users = await response.json()
#                     for user in users:
#                         if user.get("tg_id") == tg_id:
#                             user_id = user.get("id")
#                             api_url_projects = base_url + view_projects
#                             async with session.get(api_url_projects, ssl=False) as response_projects:
#                                 if response_projects.status == 200:
#                                     try:
#                                         projects_data = await response_projects.json()
#                                         user_projects = [
#                                             project for project in projects_data if user_id in [
#                                                 user.get("id") for user in project.get("users")
#                                             ]
#                                         ]
#                                         project_ids = [project.get("id") for project in user_projects]
#                                         return (
#                                             user.get("username"),
#                                             user_projects,
#                                             user_id,
#                                             project_ids,
#                                             user_projects[0].get("id") if user_projects else None
#                                         )
#                                     except json.JSONDecodeError:
#                                         pass
#                 except json.JSONDecodeError:
#                     pass

#     return None, None, None, None, None


# async def is_valid_username(username):
#     # Проверка требований к имени пользователя
#     if not re.match(r"^[a-zA-Z0-9_]+$", username):
#         return False

#     return True


# # Функция для проверки формата даты
# def is_valid_date(date):
#     pattern = r"\d{4}-\d{2}-\d{2}"
#     return re.match(pattern, date) is not None


# # Функция для проверки количества часов
# def is_valid_hours(hours):
#     pattern = r"\d{1,2}"
#     return re.match(pattern, hours) is not None

# def is_back(message):
#     if message.lower() == 'назад':
#         return True
#     else:
#         return False
    
