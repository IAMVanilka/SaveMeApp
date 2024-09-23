import configparser
import logging
import time
import psutil
from colorama import Fore, Style
from scripts import config_manager, upload_download_data, logger_config, console_UI

logger_config.setup_logging()
logger = logging.getLogger(__name__)


def check_if_process_running(process_name):
    # Проходим по всем запущенным процессам
    for proc in psutil.process_iter():
        try:
            # Получаем имя процесса через атрибут .name()
            if process_name.lower() in proc.name().lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False


def auto_send_saves(drive):
    # Создаем объект ConfigParser
    config = configparser.ConfigParser()
    config.read('paths_config.ini')

    exe_list = []

    # Перебираем все секции в конфиге
    for section in config.sections():
        if 'exe' in config[section]:
            exe = config[section]['exe']
            exe_list.append(exe)

    def send_saves(drive):
        print("| " + Fore.GREEN + "Запущен процесс отслеживания игр..." + Style.RESET_ALL + Fore.CYAN + " |")
        if not exe_list:
            logger.info("Нет игр для отслеживания.")
            return
        while True:
            #  Перебор всех exe в конфиге в поисках запущенных процессов
            for exe_file in exe_list:
                if not check_if_process_running(exe_file):
                    logger.debug("Ожидание запуска игры...")
                    time.sleep(5)
                else:
                    #  Ожидание завершения процесса
                    logger.info(f"Игра {exe_file} запущена. Процесс отслеживается.")
                    while check_if_process_running(exe_file):
                        time.sleep(10)
                    else:
                        logger.info("Игра завершена. Загрузка сохранений в облако...")

                        #  Найти секцию с текущим exe и загрузить сохранения
                        for section in config.sections():
                            if config[section].get('exe') == exe_file:
                                game_info = config_manager.get_game_info(section)
                                console_UI.run_notification('Загрузка', "Началась загрузка сохранений в облако...")

                                up_res = upload_download_data.upload(section, game_info[0], drive)

                                if up_res == False:
                                    logger.error("ОШИБКА! Сохранения не загружены в облако или загружены с ошибкой!")
                                    console_UI.run_notification("ОШИБКА!", "Сохранения не загружены в облако или "
                                                                       "загружены с ошибкой!")

                                else:
                                    logger.info("Сохранения загружены в облако.")
                                    console_UI.run_notification("Успех!", "Сохранения успешно загружены!")

                                break

    send_saves(drive)
