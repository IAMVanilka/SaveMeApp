from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from colorama import Fore, Style, init

import os


def google_auth():
    init()

    # Определите область доступа
    SCOPES = ['https://www.googleapis.com/auth/drive']

    # Файл токенов
    creds_file = 'tokens/user_token.json'
    client_secrets_file = 'tokens/client_secrets.json'
    creds = None

    # Попытка загрузить локальные токены (если есть)
    if os.path.exists(creds_file):
        creds = Credentials.from_authorized_user_file(creds_file, SCOPES)

    if not os.path.exists(client_secrets_file):
        print(f"{Fore.RED}!!!'client_secrets.json' не найден!!!{Style.RESET_ALL}")
        input(f"{Fore.CYAN}!!!Нажмите Enter для выхода!!!{Style.RESET_ALL}")

    # Если токены не найдены или истекли, запускаем процесс аутентификации
    if not creds or not creds.valid:

        print(f"{Fore.RED}!!!Токен авторизации не найден или истек. Пожалуйста, пройдите авторизацию.!!! (Сейчас "
              f"должен открыться браузер для авторизации){Style.RESET_ALL}")

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'tokens/client_secrets.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # Сохраняем токены для повторного использования
        with open(creds_file, 'w') as token:
            token.write(creds.to_json())

    return creds
