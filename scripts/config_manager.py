import configparser

from colorama import Fore, Style, init

from scripts import upload_download_data


# Инициализация colorama
init()

def read_config(file_path):
    config = configparser.ConfigParser()
    config.read(file_path)
    return config


def delete_section(game_name):
    config = read_config(upload_download_data.resource_path('paths_config.ini'))
    if game_name in config:
        config.remove_section(game_name)
        with open(upload_download_data.resource_path('paths_config.ini'), 'w') as configfile:
            config.write(configfile)
        print(Fore.GREEN + f"Конфигурация '{game_name}' успешно удалена." + Style.RESET_ALL)
    else:
        print(Fore.RED + f"Игра '{game_name}' не найдена в конфиге." + Style.RESET_ALL)


def display_games():
    """Отображает список игр и их параметры из конфигурационного файла."""
    config = read_config(upload_download_data.resource_path('paths_config.ini'))

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



def get_game_info(game_name):
    config = read_config(upload_download_data.resource_path('paths_config.ini'))
    saves_path = config.get(game_name, 'saves_path')
    exe_path = config.get(game_name, 'game_path')
    exe = config.get(game_name, 'exe')
    return saves_path, exe_path + exe
