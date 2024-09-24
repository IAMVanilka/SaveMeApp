# MIT License
# Copyright (c) 2024 IAMVanilka

from colorama import Fore, Style, init

init()

def folder_exists(folder_name, drive_service, parent_folder=None):
    """Проверка наличия папки на Google Drive. При указании parent_folder, проверяется наличие папки в родительской
    папке."""
    if parent_folder is not None:
        query = (f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' and '{parent_folder}' "
                 f"in parents and trashed = false")
    else:
        query = f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"

    results = drive_service.files().list(q=query).execute()
    folder_list = results.get('files', [])

    if folder_list:
        folder_id = folder_list[0]['id']
        return True, folder_id
    else:
        return False, folder_list


def add_saves_directory(drive_service, game_name):
    # Проверяем наличие основной папки
    main_folder_exists, main_folder_id = folder_exists('SaveMeApp', drive_service)

    if not main_folder_exists:
        print("Основная папка 'SaveMeApp' не найдена.")
        return None

    def create_save_directory():
        # Проверяем наличие папки для игры
        existing_folder_exists, existing_folder_id = folder_exists(game_name, drive_service, main_folder_id)

        if existing_folder_exists:
            print(f"Папка '{Fore.GREEN + game_name + Style.RESET_ALL}' уже существует с ID: {Fore.GREEN + existing_folder_id + Style.RESET_ALL}")
            return existing_folder_id
        else:
            # Создание новой папки
            folder_metadata = {
                'name': game_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [main_folder_id]  # Указание родительской папки
            }
            folder = drive_service.files().create(body=folder_metadata, fields='id').execute()
            print(
                f'Создана папка с именем "{Fore.GREEN + game_name + Style.RESET_ALL}" и ID: {Fore.GREEN + folder["id"] + Style.RESET_ALL} в папке "SaveMeApp" с ID: {Fore.GREEN + main_folder_id + Style.RESET_ALL}')

            return folder["id"]

    return create_save_directory()

def remove_saves_directory(drive_service, game_name):
    """Удаляет папку в Google Drive по её ID."""
    from googleapiclient.errors import HttpError

    print(Fore.YELLOW + "Удаление папки в облаке..." + Style.RESET_ALL)

    folder_id = find_folder_id(drive_service, game_name)

    try:
        drive_service.files().delete(fileId=folder_id).execute()
        print(f"-Папка с ID {Fore.GREEN + folder_id + Style.RESET_ALL} успешно удалена.")
    except HttpError as e:
        print(Fore.RED + f"- Ошибка при удалении папки: {e}" + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"- Произошла непредвиденная ошибка: {e}" + Style.RESET_ALL)



def create_main_folder(drive):
    main_folder_id = folder_exists('SaveMeApp', drive)
    if main_folder_id[0]:
        print(Fore.YELLOW + "Папка 'SaveMeApp' уже существует" + Style.RESET_ALL)
        return main_folder_id[1]
    else:
        # Создание главной директории если ее нет
        folder_metadata = {
            'title': 'SaveMeApp',
            'mimeType': 'application/vnd.google-apps.folder'
        }
        main_folder = drive.CreateFile(folder_metadata)
        main_folder.Upload()

        print(Fore.GREEN + f'Создана папка с ID: {Fore.BLUE + main_folder["id"] + Style.RESET_ALL}' + Style.RESET_ALL)

        return main_folder["id"]


def find_folder_id(drive_service, folder_name=None):
    def get_main_folder_id(drive_service):
        # Поиск папки 'SaveMeApp' в корневой директории
        query = "name='SaveMeApp' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        results = drive_service.files().list(q=query, fields="files(id, name)").execute()
        items = results.get('files', [])
        if items:
            # Вернуть ID первой найденной папки
            return items[0]['id']
        else:
            print(Fore.RED + "Папка " + Fore.BLUE + "'SaveMeApp'" + Style.RESET_ALL + " не найдена." + Style.RESET_ALL)
            return None

    if folder_name is None:
        main_folder_id = get_main_folder_id(drive_service)
        return main_folder_id
    else:
        main_folder_id = get_main_folder_id(drive_service)

        # Поиск указанной папки в 'SaveMeApp'
        query = (f"name='{folder_name}' and '{main_folder_id}' in parents and mimeType='application/vnd.google-apps"
                 f".folder' and trashed=false")
        results = drive_service.files().list(q=query, fields="files(id, name)").execute()
        items = results.get('files', [])
        if items:
            return items[0]['id']
        else:
            print(Fore.RED + f"Папка с именем '{Fore.BLUE + folder_name + Style.RESET_ALL}' не найдена в 'SaveMeApp'." + Style.RESET_ALL)
            return None


def list_files_in_folder(drive_service, folder_name=None):
    if folder_name is not None:
        folder_id = find_folder_id(drive_service, folder_name)
        if folder_id:
            # Поиск файлов в указанной папке
            query = f"'{folder_id}' in parents and trashed=false"
            results = drive_service.files().list(q=query, fields="files(id, name)").execute()
            file_list = results.get('files', [])
            files = [file['name'] for file in file_list]
            return files
        else:
            return []
    else:
        # Поиск файлов в корневой папке
        query = "'root' in parents and trashed=false"
        results = drive_service.files().list(q=query, fields="files(id, name)").execute()
        file_list = results.get('files', [])
        files = [file['name'] for file in file_list]
        return files


def delete_save(drive_service, game_name, save_name):
    # Поиск папки игры
    folder_id = find_folder_id(drive_service, game_name)
    if not folder_id:
        print(Fore.RED + f"Папка с именем '{game_name}' не найдена." + Style.RESET_ALL)
        return

    # Поиск файла сохранения
    query = f"name='{save_name}' and '{folder_id}' in parents and trashed=false"
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    items = results.get('files', [])
    if items:
        file_id = items[0]['id']
        drive_service.files().delete(fileId=file_id).execute()
        print(Fore.GREEN + f"Файл '{save_name}' успешно удален." + Style.RESET_ALL)
    else:
        print(Fore.RED + f"Файл '{save_name}' не найден в папке '{game_name}'." + Style.RESET_ALL)
