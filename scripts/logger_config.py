# MIT License
# Copyright (c) 2024 IAMVanilka

import os
import logging
import sys
from datetime import datetime
from pathlib import Path

from scripts import upload_download_data, config_manager


def setup_logging():
    config = config_manager.read_config(upload_download_data.resource_path('settings.ini'))

    # Путь к родительской директории
    script_dir = Path(sys.executable).resolve()  # Текущая директория скрипта

    # Создаёт папку logs в родительской директории
    log_dir = upload_download_data.resource_path('logs')
    os.makedirs(log_dir, exist_ok=True)

    # Создает лог-файл с датой
    date_str = datetime.now().strftime('%Y-%m-%d')
    log_file = os.path.join(log_dir, f'Save_Me_log_{date_str}.log')

    # Настройка логгера
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)  # Устанавливаем уровень логирования

    # Создание обработчиков
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    console_handler = logging.StreamHandler()

    # Уровни логирования
    file_handler.setLevel(logging.INFO)
    if config.get('Settings', 'console_log') == 'on':
        console_handler.setLevel(logging.INFO)
    else:
        console_handler.setLevel(logging.ERROR)

    # Форматирование сообщений
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Очистка предыдущих обработчиков
    if logger.hasHandlers():
        logger.handlers.clear()

    # Добавление обработчиков
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
