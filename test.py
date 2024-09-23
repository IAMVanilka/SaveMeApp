import sys
from pathlib import Path


def resource_path(relative_path=""):
    """Определяет абсолютный путь к ресурсу в собранном приложении или меняет путь, если запуск в режиме разработки."""
    if getattr(sys, 'frozen', False):
        # Для сборки с PyInstaller
        base_path = Path(sys.executable).resolve().parent
    else:
        # Для запуска в разработке
        base_path = Path(__file__).resolve().parent
    return base_path / relative_path


print(Path(sys.executable).resolve().parent)