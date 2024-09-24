# MIT License
# Copyright (c) 2024 IAMVanilka

import os
import shutil
import zipfile


def zip_folder(path):
    # Создайте ZIP-архив
    shutil.make_archive(path.replace('.zip', ''), 'zip', path)


def unzip_file(zip_file_path, extract_to):
    # Получить имя архива без расширения
    archive_name = os.path.basename(zip_file_path).replace('.zip', '')

    # Путь для распаковки: если не указан, создаем папку с именем архива
    if extract_to is None:
        extract_to = os.path.join(os.path.dirname(zip_file_path), archive_name)

    # Если папка не существует, создать её
    if not os.path.exists(extract_to):
        os.makedirs(extract_to)

    try:
        # Открыть архив
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            # Распаковать все файлы
            zip_ref.extractall(extract_to)
            print(f"Файлы успешно распакованы в {extract_to}")
    except zipfile.BadZipFile:
        print(f"Ошибка: {zip_file_path} не является допустимым архивом.")
    except Exception as e:
        print(f"Ошибка распаковки: {e}")

    #  Удаление архива
    os.remove(zip_file_path)
