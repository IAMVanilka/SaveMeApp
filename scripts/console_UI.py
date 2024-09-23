import time

from win10toast import ToastNotifier

from scripts import config_manager, actions

from colorama import init, Fore, Style
from termcolor import colored


def notification(title, message, duration=10):
    toaster = ToastNotifier()
    toaster.show_toast(
        title,
        message,
        duration=duration
    )


def display_menu():
    # Верхняя граница
    print(Fore.CYAN + Style.BRIGHT + "+" + "-" * 35 + "+")

    # Заголовок
    print("|" + " " * 10 + Fore.YELLOW + "Главное меню" + " " * 10 + "|")

    # Основной текст меню
    print(Fore.CYAN + "+" + "-" * 35 + "+")
    print(Fore.CYAN + "+" + "-" * 35 + "+")
    print(Fore.YELLOW + "1." + Fore.RESET + " Скачать сохранения из облака")
    print(Fore.YELLOW + "2." + Fore.RESET + " Загрузить сохранения в облако")
    print(Fore.YELLOW + "3." + Fore.RESET + " Список игр")
    print(Fore.YELLOW + "4." + Fore.RESET + " Настройки")
    print(Fore.YELLOW + "0." + Fore.RESET + " Выход")

    # Нижняя граница
    print(Fore.CYAN + "+" + "-" * 35 + "+" + Style.RESET_ALL)

    # Ввод пользователя
    print(Fore.CYAN + Style.BRIGHT + "Выберите пункт меню: " + Style.RESET_ALL, end='')


class MainMenu:
    def __init__(self):
        self.gauth = None
        self.drive = None

    def input_handler(self):
        while True:
            display_menu()

            choice = input(">>")
            if choice == "1":
                print(Fore.GREEN + "[СКАЧИВАНИЕ СОХРАНЕНИЙ]" + Style.RESET_ALL)
                config_manager.display_games()
                game_name = input(Fore.YELLOW + "Напишите название игры: " + Style.RESET_ALL)

                actions.download_saves(game_name, self.drive)

                input(Fore.CYAN + 'Операция завершена. Нажмите "Enter" для продолжения.' + Style.RESET_ALL)
            elif choice == "2":
                print(Fore.GREEN + "[ЗАГРУЗКА СОХРАНЕНИЙ]" + Style.RESET_ALL)
                config_manager.display_games()
                game_name = input(Fore.YELLOW + "Напишите название игры: " + Style.RESET_ALL)

                actions.upload_saves(game_name, self.drive)

                input(Fore.CYAN + 'Операция завершена. Нажмите "Enter" для продолжения.' + Style.RESET_ALL)
            elif choice == "3":
                actions.show_list_of_games(self.drive)
            elif choice == "4":
                actions.open_settings()
            elif choice == '0':
                print(Fore.RED + "Выход из программы..." + Style.RESET_ALL)
                time.sleep(1)
                break
            else:
                print(Fore.RED + "Используйте цифры от 1 до 4 для выбора раздела меню!" + Style.RESET_ALL)

    def run(self):
        self.input_handler()
