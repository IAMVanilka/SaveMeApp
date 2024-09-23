from colorama import Fore, Style, init
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from googleapiclient.errors import HttpError
from datetime import datetime
from pathlib import Path
from tqdm import tqdm
import sys
import os

from scripts import drive_manager, zip_files

init()

def resource_path(relative_path):
    """Определяет абсолютный путь к ресурсу в собранном приложении или меняет путь, если запуск в режиме разработки."""
    if getattr(sys, 'frozen', False):
        # Для сборки с PyInstaller
        base_path = Path(sys.executable).resolve().parent
    else:
        # Для запуска в разработке
        base_path = Path(__file__).resolve().parent.parent
    return base_path / relative_path


def get_file_ids(file_name, drive_service, parent_folder_id=None):
    """Получает ID файлов с заданным именем"""
    if parent_folder_id is not None:
        # Поиск в родительской папке по имени
        query = f"name='{file_name}' and '{parent_folder_id}' in parents and trashed=false"
        results = drive_service.files().list(q=query).execute()
        return [file['id'] for file in results.get('files', [])]
    else:
        query = f"name='{file_name}' and trashed=false"
        results = drive_service.files().list(q=query).execute()
        return [file['id'] for file in results.get('files', [])]


def find_file_id(file_name, folder_id, drive_service):
    query = f"name='{file_name}' and '{folder_id}' in parents and trashed=false"
    try:
        file_list = drive_service.files().list(q=query).execute()
        if file_list.get('files'):
            return file_list['files'][0]['id']
        else:
            print(Fore.YELLOW + f"Файл с именем {file_name} не найден в папке с ID: {folder_id}" + Style.RESET_ALL)
            return None
    except HttpError as error:
        print(Fore.RED + f"Произошла ошибка: {error}" + Style.RESET_ALL)
        return None


def delete_duplicate(file_ids, drive_service):
    """Удаляет дубликаты файлов по их ID."""""
    for file_id in file_ids:
        try:
            drive_service.files().delete(fileId=file_id).execute()
            print(Fore.GREEN + f"Удаление старого файла с ID: {file_id} завершено." + Style.RESET_ALL)
        except Exception as error:
            print(Fore.RED + f"Ошибка удаления файла с ID {file_id}: {error}" + Style.RESET_ALL)


def download_config(drive_service):
    try:
        local_path = resource_path('paths_config.ini')

        if not os.path.exists(os.path.dirname(local_path)):
            os.makedirs(os.path.dirname(local_path))

        main_folder_id = drive_manager.find_folder_id(drive_service)
        if not main_folder_id:
            raise FileNotFoundError("Основная папка SaveMeApp не найдена.")

        file_id = find_file_id('paths_config.ini', main_folder_id, drive_service)
        if not file_id:
            raise FileNotFoundError("Файл 'paths_config.ini' не найден в папке SaveMeApp.")

        with open(local_path, 'w') as file:
            file.write("")

        request = drive_service.files().get_media(fileId=file_id)
        with open(local_path, 'wb') as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                if status:
                    print(Fore.CYAN + f"Загружено {int(status.progress() * 100)}%." + Style.RESET_ALL)

        print(Fore.GREEN + f"Файл 'paths_config.ini' успешно загружен в {local_path}." + Style.RESET_ALL)

    except FileNotFoundError as fnf_error:
        print(Fore.RED + f"Ошибка: {fnf_error}" + Style.RESET_ALL)
    except HttpError as http_err:
        print(Fore.RED + f"Произошла ошибка при взаимодействии с API Google Drive: {http_err}" + Style.RESET_ALL)
    except OSError as os_err:
        print(Fore.RED + f"Ошибка файловой системы: {os_err}" + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"Произошла неизвестная ошибка: {e}" + Style.RESET_ALL)


def upload_config(drive_service):
    try:
        folder_id = drive_manager.find_folder_id(drive_service)
        old_configs = get_file_ids('paths_config.ini', drive_service, folder_id)

        file_path = resource_path('paths_config.ini')
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Файл {file_path} не найден.")

        file_metadata = {'name': 'paths_config.ini', 'parents': [folder_id]}
        media = MediaFileUpload(file_path, mimetype='text/plain')

        drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        print(Fore.GREEN + "-Конфиг файл успешно загружен в облако." + Style.RESET_ALL)

        delete_duplicate(old_configs, drive_service)

    except FileNotFoundError as e:
        print(Fore.RED + f"Ошибка: {e}" + Style.RESET_ALL)
    except HttpError as e:
        print(Fore.RED + f"Ошибка HTTP: {e}" + Style.RESET_ALL)
    except OSError as e:
        print(Fore.RED + f"Ошибка файловой системы: {e}" + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"Произошла непредвиденная ошибка: {e}" + Style.RESET_ALL)


def upload(game_name, file_path, drive_service):
    current_time = datetime.now().strftime("|%d-%m-%Y_%H:%M")
    print(Fore.GREEN + '-Создание архива...' + Style.RESET_ALL)
    zip_files.zip_folder(file_path)
    print(Fore.GREEN + "-Архив успешно создан" + Style.RESET_ALL)

    folder_id = drive_manager.add_saves_directory(drive_service, game_name)
    path = file_path.split("\\")
    old_saves_ids = get_file_ids(path[::-1][0] + '.zip', drive_service)

    try:
        zip_file_path = file_path + '.zip'
        file_size = os.path.getsize(zip_file_path)

        file_metadata = {'name': path[::-1][0] + current_time + '.zip', 'parents': [folder_id]}
        media = MediaFileUpload(zip_file_path, mimetype='application/zip', resumable=True)
        request = drive_service.files().create(body=file_metadata, media_body=media, fields='id')

        response = None
        with tqdm(total=file_size, unit='B', unit_scale=True, desc="Загрузка " + path[::-1][0] + '.zip') as pbar:
            while response is None:
                status, response = request.next_chunk()
                if status:
                    pbar.update(int(status.resumable_progress) - pbar.n)

        print(Fore.GREEN + f"Файл " + Fore.CYAN + f"{zip_file_path} " + Fore.GREEN + f"успешно загружен с ID: " + Fore.YELLOW + f"{response['id']}" + Style.RESET_ALL)

        media._fd.close()

    finally:
        try:
            os.remove(file_path + '.zip')
            print(Fore.GREEN + f"Файл '{file_path}.zip' удален." + Style.RESET_ALL)
            return True
        except PermissionError as e:
            print(Fore.RED + f"Ошибка при удалении файла: {e}" + Style.RESET_ALL)
            return False
        except FileNotFoundError:
            print(Fore.RED + f"Файл '{file_path}' не существует." + Style.RESET_ALL)
            return False
        except Exception as e:
            print(Fore.RED + f"Непредвиденная ошибка: {e}" + Style.RESET_ALL)

    if old_saves_ids:
        delete_duplicate(old_saves_ids, drive_service)

    return True


def download(file_name, local_path, drive_service, cfg_section):
    def find_main_folder_id(folder_name, drive_service, parent_folder_id=None):
        if parent_folder_id is not None:
            query = (f"name='{folder_name}' and '{parent_folder_id}' in parents and mimeType='application/vnd.google"
                     f"-apps.folder' and trashed=false")
            try:
                folder_list = drive_service.files().list(q=query).execute()
                if folder_list.get('files'):
                    return folder_list['files'][0]['id']
                else:
                    print(Fore.YELLOW + f"Папка с названием '{folder_name}' не найдена в '{parent_folder_id}'" + Style.RESET_ALL)
                    return None
            except HttpError as error:
                print(Fore.RED + f"Произошла ошибка: {error}" + Style.RESET_ALL)
                return None

        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        try:
            folder_list = drive_service.files().list(q=query).execute()
            if folder_list.get('files'):
                return folder_list['files'][0]['id']
            else:
                print(Fore.YELLOW + f"Папка с таким названием не найдена: {folder_name}" + Style.RESET_ALL)
                return None
        except HttpError as error:
            print(Fore.RED + f"Произошла ошибка: {error}" + Style.RESET_ALL)
            return None

    main_folder_id = find_main_folder_id('SaveMeApp', drive_service)
    saves_folder_id = find_main_folder_id(cfg_section, drive_service, main_folder_id)

    if saves_folder_id:
        file_id = find_file_id(file_name, saves_folder_id, drive_service)
        if file_id:
            try:
                request = drive_service.files().get_media(fileId=file_id)
                with open(local_path, 'wb') as fh:
                    downloader = MediaIoBaseDownload(fh, request)
                    done = False
                    while not done:
                        status, done = downloader.next_chunk()
                        print(Fore.CYAN + f"Загружено {int(status.progress() * 100)}%." + Style.RESET_ALL)
                print(Fore.GREEN + f"Файл {file_name} успешно загружен в {local_path}." + Style.RESET_ALL)
            except HttpError as e:
                print(Fore.RED + f"Ошибка при загрузке файла: {e}" + Style.RESET_ALL)
    return True
