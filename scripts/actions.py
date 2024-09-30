# MIT License
# Copyright (c) 2024 IAMVanilka

import logging
import os

from colorama import Fore, Style, init

from scripts import config_manager, upload_download_data, zip_files, drive_manager, logger_config
from scripts.config_manager import read_config

logger_config.setup_logging()
logger = logging.getLogger(__name__)

# Инициализация colorama
init()


class Menu:

    def __init__(self, title, menu_items, exit_btn=True):
        self.title = title
        self.menu_items = menu_items
        self.exit_menu = exit_btn

    def display_menu(self):
        """Отображает меню с оформлением."""
        # Верхняя граница
        print(Fore.CYAN + Style.BRIGHT + "\n+" + "-" * 35 + "+")

        # Заголовок
        print("|" + " " * ((35 - len(self.title)) // 2) + Fore.YELLOW + self.title + " " * (
                (35 - len(self.title)) // 2) + "|")

        # Основной текст меню
        print(Fore.CYAN + "+" + "-" * 35 + "+" + Style.RESET_ALL)

        for key, (description_func, _) in self.menu_items.items():
            # Проверяем, callable ли объект, прежде чем пытаться вызвать его
            if callable(description_func):
                description = description_func()  # Получаем актуальное описание
            else:
                description = str(description_func)  # Преобразуем в строку, если это не функция

            # Печатаем пункт меню с цветом
            print(Fore.YELLOW + f"{key}." + Fore.RESET + f" {description}")

        # Нижняя граница
        print(Fore.CYAN + "+" + "-" * 35 + "+" + Style.RESET_ALL)

        # Ввод пользователя
        print(Fore.CYAN + Style.BRIGHT + "Выберите пункт меню: " + Style.RESET_ALL, end='')

    def run(self):
        """Запуск цикла меню."""
        if self.exit_menu:
            self.menu_items['0'] = ("Выход", self.close_menu)

        while True:
            self.display_menu()
            user_input = input()

            if user_input in self.menu_items:
                _, action = self.menu_items[user_input]
                action()  # Вызов функции, привязанной к пункту меню

                if action == self.close_menu:
                    break
            else:
                print("Неверный ввод. Попробуйте снова.")

    def close_menu(self):
        """Функция для выхода из меню."""
        print("")


class SettingsSection:
    """Класс для работы с секцией настроек."""

    def __init__(self, config, section, key, name):
        self.setting_name = name
        self.config = config
        self.section = section
        self.key = key

    def display_setting(self):
        """Возвращает строку с названием настройки и её статусом."""
        status = self.get_setting_status()
        res = f"{self.setting_name}: {status}"
        return res

    def get_setting_status(self):
        """Получает статус настройки."""
        try:
            return self.config.get(self.section, self.key)
        except KeyError:
            print(
                Fore.RED + Style.BRIGHT + f"\n[Ошибка] Отсутствует ключ '{self.key}' в секции '{self.section}'!" + Style.RESET_ALL)
            return None

    def _save_config(self):
        try:
            with open('settings.ini', 'w') as configfile:
                self.config.write(configfile)
            print(Fore.GREEN + Style.BRIGHT + "[Успешно] Настройки сохранены." + Style.RESET_ALL)
        except IOError as e:
            print(Fore.RED + Style.BRIGHT + f"\n[Ошибка] При записи настроек: {e}" + Style.RESET_ALL)

    def toggle_setting_status(self):
        """Переключает статус настройки."""
        current_status = self.get_setting_status()
        if current_status is None:
            return  # Если произошла ошибка, выходим

        new_status = "off" if current_status == "on" else "on"
        self.config[self.section][self.key] = new_status
        self._save_config()
        print(
            Fore.YELLOW + f"\n[Изменено] Настройка [{self.setting_name}] переключена на {new_status}." + Style.RESET_ALL)
        input(Fore.CYAN + "Нажмите Enter для продолжения..." + Style.RESET_ALL)

    def set_setting_status(self, status):
        """Устанавливает введенное пользователем значение настройки."""
        self.config[self.section][self.key] = str(status)
        self._save_config()
        print(Fore.YELLOW + f"\n[Изменено] Настройка [{self.setting_name}] установлена на {status}." + Style.RESET_ALL)
        input(Fore.CYAN + "Нажмите Enter для продолжения..." + Style.RESET_ALL)

    def waiting_for_input(self):
        """Ожидает ввода пользователя для подтверждения или отмены действия."""
        while True:
            print(Fore.CYAN + "\nВведите новое значение для настройки или введите 'n' для выхода." + Style.RESET_ALL)
            user_input = input(Fore.CYAN + ">> " + Style.RESET_ALL)
            if user_input.lower() == 'n':
                break
            else:
                try:
                    self.set_setting_status(int(user_input))
                    break
                except ValueError:
                    print(
                        Fore.RED + Style.BRIGHT + "\n[Ошибка] Неверный формат ввода! Введите значение в цифрах." + Style.RESET_ALL)


def download_saves(game_name, drive):
    try:
        # Чтение конфига
        config = config_manager.read_config(upload_download_data.resource_path('paths_config.ini'))
        if game_name not in config:
            raise KeyError(f"Игра '{game_name}' не найдена в конфигурации!")

        # Получение пути к сохранениям
        saves_path = config.get(game_name, 'saves_path')
        if not saves_path:
            raise ValueError(f"Путь к сохранениям для игры '{game_name}' не указан в конфигурации.")

        print(Fore.CYAN + 'Загрузка списка сохранений...' + Style.RESET_ALL)

        # Проверка существования пути для сохранений
        if not os.path.exists(saves_path):
            raise FileNotFoundError(f"Директория {saves_path} не существует.")

        def get_list_of_saves(drive, game_name):
            """Получение списка сохраненных игр"""
            list_of_saves = drive_manager.list_files_in_folder(drive, game_name)

            print(Fore.CYAN + 'Сохраненные игры:' + Style.RESET_ALL)
            for index, save in enumerate(list_of_saves, start=1):
                print(f"{index}. {save}")

            user_input = input(Fore.CYAN + "Введите номер сохраненной игры или '0' для выхода: " + Style.RESET_ALL)
            if user_input == "0":
                return None
            elif not user_input.isdigit() or int(user_input) not in range(1, len(list_of_saves) + 1):
                raise ValueError("Некорректный ввод. Введите число от 1 до " + str(len(list_of_saves)))
            selected_save = list_of_saves[int(user_input) - 1]
            print(Fore.YELLOW + f"Выбранное сохранение: {Fore.BLUE + selected_save + Style.RESET_ALL}" + Style.RESET_ALL)
            print(f"{Fore.YELLOW}Ожидание начала загрузки сохранения...{Style.RESET_ALL}")

            return selected_save

        save_name = get_list_of_saves(drive, game_name)

        if save_name is not None:
            # Скачивание файла
            download_result = upload_download_data.download(save_name, saves_path + '.zip', drive,
                                                            cfg_section=game_name)
            if not download_result:
                raise IOError("Ошибка при скачивании файла!")

            # Распаковка архива
            zip_files.unzip_file(saves_path + '.zip', saves_path)
            print(f"{Fore.GREEN}Сохранения для '{Fore.BLUE + game_name + Style.RESET_ALL}' успешно загружены и "
                               f"распакованы." + Style.RESET_ALL)

    except KeyError as e:
        print(Fore.RED + Style.BRIGHT + f"Ошибка: {e}. Проверьте, что игра добавлена в конфигурацию." + Style.RESET_ALL)
    except ValueError as e:
        print(Fore.RED + Style.BRIGHT + f"Ошибка: {e}. Путь к сохранениям не указан корректно." + Style.RESET_ALL)
    except FileNotFoundError as e:
        print(
            Fore.RED + Style.BRIGHT + f"Ошибка: {e}. Убедитесь, что директория сохранений существует." + Style.RESET_ALL)
    except IOError as e:
        print(Fore.RED + Style.BRIGHT + f"Ошибка: {e}. Не удалось скачать или распаковать файл." + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + Style.BRIGHT + f"Непредвиденная ошибка: {e}." + Style.RESET_ALL)


def upload_saves(game_name, drive):
    try:
        # Чтение конфига
        config = config_manager.read_config(upload_download_data.resource_path('paths_config.ini'))
        settings_config = config_manager.read_config(upload_download_data.resource_path('settings.ini'))

        if game_name not in config:
            raise KeyError(f"Игра '{game_name}' не найдена в конфигурации!")

        # Получение пути к сохранениям
        file_path = config.get(game_name, 'saves_path')
        if not file_path:
            raise ValueError(f"Путь к сохранениям для игры '{game_name}' не указан в конфигурации.")

        # Проверка существования директории для сохранений
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Директория {file_path} не существует.")

        file_name = file_path.split('\\')
        zip_file_name = file_name[::-1][0] + '.zip'
        print(Fore.YELLOW + f'Загрузка в облако: {zip_file_name}...' + Style.RESET_ALL)

        list_of_saves = drive_manager.list_files_in_folder(drive, game_name)
        max_saves = settings_config.get("Settings", "max_saves")
        if len(list_of_saves) > int(max_saves):
            print(Fore.RED + f'Сохранений в папке {Fore.BLUE + game_name + Style.RESET_ALL} больше {Fore.BLUE + max_saves + Style.RESET_ALL}. Автоматическое удаление старых сохранений...' + Style.RESET_ALL)
            logger.info(f'Директория {game_name}. Удаление старых сохранений в облаке...')
            while len(list_of_saves) > max_saves:
                list_of_saves = drive_manager.list_files_in_folder(drive, game_name)
                drive_manager.delete_save(drive, game_name, list_of_saves[-1])

        # Загрузка файла в облако
        upload_result = upload_download_data.upload(game_name, file_path, drive)

        if upload_result == False:
            raise IOError("Ошибка при загрузке файла в облако!")

        print(Fore.GREEN + f"Сохранения для '{Fore.BLUE + game_name + Style.RESET_ALL}' успешно загружены в облако." + Style.RESET_ALL)

    except KeyError as e:
        print(Fore.RED + f"Ошибка: {e}. Проверьте, что игра добавлена в конфигурацию." + Style.RESET_ALL)
    except ValueError as e:
        print(Fore.RED + f"Ошибка: {e}. Путь к сохранениям не указан корректно." + Style.RESET_ALL)
    except FileNotFoundError as e:
        print(Fore.RED + f"Ошибка: {e}. Убедитесь, что директория сохранений существует." + Style.RESET_ALL)
    except IOError as e:
        print(Fore.RED + f"Ошибка: {e}. Не удалось загрузить файл в облако." + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"Непредвиденная ошибка: {e}." + Style.RESET_ALL)


def open_settings():
    # try:
    #     # Чтение конфигурации
    config = config_manager.read_config(upload_download_data.resource_path('settings.ini'))

    auto_deleting_setting = SettingsSection(config, "Settings", "saves_deleting", "Автоудаление сохранений")
    auto_send_saves_setting = SettingsSection(config, "Settings", "autosave", "Автосохранение в облако")
    max_saves_setting = SettingsSection(config, "Settings", "max_saves", "Количество хранимых сохранений в облаке")
    logs_setting = SettingsSection(config, "Settings", "console_log", "Отображать логи в консоль")

    settings_menu = Menu(
        title='НАСТРОЙКИ',
        menu_items={
            '1': (auto_send_saves_setting.display_setting, auto_send_saves_setting.toggle_setting_status),
            '2': (auto_deleting_setting.display_setting, auto_deleting_setting.toggle_setting_status),
            '3': (max_saves_setting.display_setting, max_saves_setting.waiting_for_input),
            '4': (logs_setting.display_setting, logs_setting.toggle_setting_status)
        }
    )

    settings_menu.run()


def show_list_of_games(drive):
    def path_checker(path):
        if os.path.exists(path):
            return True
        elif os.path.isfile(path) and path.endswith('.exe'):
            print(path)
            return True
        else:
            return False

    def show_list():
        config = read_config(upload_download_data.resource_path('paths_config.ini'))

        if not config.sections():
            print(Fore.RED + Style.BRIGHT + "Файл конфигурации пуст или отсутствует." + Style.RESET_ALL)
            print("     Вы можете добавить в него записи через предыдущее меню\n"
                  "     Или подгрузить его из облака, если вы уже использовали SaveMeApp ранее.")
            input_data = input(Fore.YELLOW + "Загрузить конфигурационный файл из облака? (y/n)\n" + Style.RESET_ALL)

            if input_data.lower() == 'y':
                upload_download_data.download_config(drive)
                input(Fore.CYAN + "Нажмите Enter для продолжения..." + Style.RESET_ALL)
                return
            else:
                return

        print(Fore.GREEN + Style.BRIGHT + "СПИСОК ДОБАВЛЕННЫХ ИГР:" + Style.RESET_ALL)
        for section, parameters in config.items():
            if section == "DEFAULT":
                continue
            print(Fore.YELLOW + f"  Игра: [{section}]" + Style.RESET_ALL)
            for key, value in parameters.items():
                if key == "game_path":
                    print(Fore.CYAN + "    Директория игры:" + Style.RESET_ALL, value)
                elif key == "saves_path":
                    print(Fore.CYAN + "    Директория сохранений:" + Style.RESET_ALL, value)
                elif key == "exe":
                    print(Fore.CYAN + "    Имя исполняемого файла:" + Style.RESET_ALL, value)

        print(Fore.MAGENTA + "\nВведите название игры, чтобы посмотреть сохранения в облаке." + Style.RESET_ALL)
        print(Fore.MAGENTA + "Или нажмите Enter для возврата в меню..." + Style.RESET_ALL)
        user_input = input(">> ")

        if user_input == "":
            print('')
            return
        else:
            list_of_saves = drive_manager.list_files_in_folder(drive, user_input)
            print(Fore.GREEN + "Сохраненные игры:" + Style.RESET_ALL)
            for index, save in enumerate(list_of_saves, start=1):
                print(f"{index}. {save}")
            input(Fore.CYAN + "Нажмите Enter для продолжения..." + Style.RESET_ALL)

    def add_games():
        config = read_config(upload_download_data.resource_path('paths_config.ini'))
        game_name = input("Напишите название игры: ")
        game_path = input("Напишите путь к директории игры: ")
        saves_path = input("Напишите путь к директории сохранений: ")
        exe = input("Напишите имя исполняемого файла: ")

        if not exe.lower().endswith('.exe'):
            exe = exe + ".exe"

        status = True
        paths = [game_path, saves_path, exe]

        #  Проверка путей
        for path in paths:
            if path.lower().endswith('.exe'):
                exe_path = os.path.join(game_path, path)
                status = path_checker(exe_path)
                if not status:
                    print(f"Путь {exe_path} не существует!")
                    input("Нажмите Enter для продолжения...")
                    break
            else:
                status = path_checker(path)
                if not status:
                    print(f"Путь {path} не существует!")
                    input("Нажмите Enter для продолжения...")
                    break

        if not status:
            return
        else:
            config[game_name] = {
                "game_path": game_path,
                "saves_path": saves_path,
                "exe": exe
            }
            with open('paths_config.ini', 'w') as configfile:
                config.write(configfile)

            drive_manager.add_saves_directory(drive, game_name)

            upload_download_data.upload_config(drive)

            print("Игра успешно добавлена в список.")
            input("Нажмите Enter для продолжения...")

    def delete_game():
        config = read_config(upload_download_data.resource_path('paths_config.ini'))

        print(Fore.YELLOW + "СПИСОК ДОБАВЛЕННЫХ ИГР:" + Style.RESET_ALL)
        for section, parameters in config.items():
            if section == "DEFAULT":
                continue
            print(Fore.GREEN + f"  Игра: [{section}]" + Style.RESET_ALL)
            for key, value in parameters.items():
                if key == "game_path":
                    print("    Директория игры: ", value)
                elif key == "saves_path":
                    print("    Директория сохранений: ", value)
                elif key == "exe":
                    print("    Имя исполняемого файла: ", value)

        print(Fore.CYAN + "Введите название игры чтобы удалить ее из списка или просто нажмите" "'Enter', чтобы "
                          "вернуться в предыдущее меню." + Style.RESET_ALL)

        user_input = input(">> ")

        if user_input == "":
            return
        elif user_input in config:
            config.pop(user_input)
            with open('paths_config.ini', 'w') as configfile:
                config.write(configfile)
            print(f"{Fore.GREEN}Игра {user_input} успешно удалена из списка!{Style.RESET_ALL}")

            print(f"Удалить папку {user_input} в облаке со всеми сохранениями внутри?(y/n)")
            user_input2 = input(">> ")

            if user_input2.lower() == 'y':
                print(
                    Fore.YELLOW + f"ВЫ УВЕРЕНЫ? ЭТО ДЕЙСТВИЕ {Fore.RED}УДАЛИТ ПАПКУ{Style.RESET_ALL} {Fore.BLUE + user_input + Style.RESET_ALL} {Fore.YELLOW}БЕЗВОЗВРАТНО СО ВСЕМИ СОХРАНЕНИЯМИ ВНУТРИ!" + Style.RESET_ALL)
                print(f"Для подтверждения введите {Fore.BLUE + user_input + Style.RESET_ALL} еще раз. Чтобы отменить "
                      f"введите {Fore.RED}'cancel'{Style.RESET_ALL}")

                while True:
                    user_input2 = input(">> ")

                    if user_input2 == user_input:
                        drive_manager.remove_saves_directory(drive, user_input)
                        upload_download_data.upload_config(drive)
                        print(Fore.GREEN + "Игра успешно удалена из списка." + Style.RESET_ALL)
                        input("Нажмите Enter для продолжения...")
                        return

                    elif user_input2 == 'cancel':
                        return
                    else:
                        print(
                            Fore.RED + f"Неверный ввод. Пожалуйста, введите название игры еще раз или введите {Fore.BLUE}'cancel'{Style.RESET_ALL} "
                                       "для выхода." + Style.RESET_ALL)
            elif user_input2.lower() == 'n':
                return
            else:
                print(Fore.RED + "Неверный ввод. Пожалуйста, введите 'y' или 'n'." + Style.RESET_ALL)
        else:
            print(Fore.RED + f"Игра {user_input} не найдена в списке." + Style.RESET_ALL)
            input("Нажмите Enter для продолжения...")
            return

    def list_of_games_menu():
        games_menu = Menu(
            title="СПИСОК ИГР",
            menu_items={
                "1": ("Добавить игру", add_games),
                "2": ("Показать список игр", show_list),
                "3": ("Удалить игру из списка", delete_game)
            }
        )

        games_menu.run()

    list_of_games_menu()
