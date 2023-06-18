import aiohttp
import json
import os
import re

async def check_existing_user(tg_id):
    # Получение абсолютного пути к файлу config.json
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, "config.json")

    # Чтение конфигурационного файла
    with open(config_path, "r") as config_file:
        config = json.load(config_file)

    drf_config = config.get("drf", {})
    base_url = drf_config.get("base_url")
    users_view = drf_config.get("users_view")
    view_projects = drf_config.get("view_projects")

    if not base_url or not users_view or not view_projects:
        return None, None, None, None, None

    # Отправка GET-запроса для получения списка пользователей
    api_url_users = base_url + users_view

    async with aiohttp.ClientSession(trust_env=True) as session:
        async with session.get(api_url_users, ssl=False) as response:
            if response.status == 200:
                try:
                    users = await response.json()
                    for user in users:
                        if user.get("tg_id") == tg_id:
                            user_id = user.get("id")
                            api_url_projects = base_url + view_projects
                            async with session.get(api_url_projects, ssl=False) as response_projects:
                                if response_projects.status == 200:
                                    try:
                                        projects_data = await response_projects.json()
                                        user_projects = [
                                            project for project in projects_data if user_id in [
                                                user.get("id") for user in project.get("users")
                                            ]
                                        ]
                                        project_ids = [project.get("id") for project in user_projects]
                                        return (
                                            user.get("username"),
                                            user_projects,
                                            user_id,
                                            project_ids,
                                            user_projects[0].get("id") if user_projects else None
                                        )
                                    except json.JSONDecodeError:
                                        pass
                except json.JSONDecodeError:
                    pass

    return None, None, None, None, None


async def is_valid_username(username):
    # Проверка требований к имени пользователя
    if not re.match(r"^[a-zA-Z0-9_]+$", username):
        return False

    return True


# Функция для проверки формата даты
def is_valid_date(date):
    pattern = r"\d{4}-\d{2}-\d{2}"
    return re.match(pattern, date) is not None


# Функция для проверки количества часов
def is_valid_hours(hours):
    pattern = r"\d{1,2}"
    return re.match(pattern, hours) is not None

def is_back(message):
    if message.lower() == 'назад':
        return True
    else:
        return False