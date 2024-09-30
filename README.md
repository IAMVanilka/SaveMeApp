# SaveMeApp

English [README](./README_en.md)

## Описание
SaveMeApp автоматизирует загрузку и синхронизацию игровых сохранений в облако (на данный момент поддерживается только Google Drive). Программа может автоматически загружать сохранения после завершения игровой сессии.

**ВНИМАНИЕ**: В ДАННЫЙ МОМЕНТ ПРОЕКТ РАБОТАЕТ ТОЛЬКО НА **WINDOWS**!

## Для обычных пользователей
Скачать exe можно по этой [ссылке](https://github.com/IAMVanilka/SaveMeApp/releases)

## Установка для разработчиков
1. Клонируйте репозиторий:
   ```-git clone https://github.com/IAMVanilka/SaveMeApp.git```
2. Перейдите в папку проекта:
   ```-cd SaveMeApp```
3. Создайте и активируйте виртуальное окружение:
   Для bash: ```python -m venv venv
			 source venv/bin/activate```
   Для cmd/dos: ```python -m venv venv
				   call venv/Scripts/activate```
4. Установите зависимости:
   ```pip install -r requirements.txt```
5. Запустите программу:
   ```python main.py```
   
## Использование
После запуска программы следуйте инструкциям в консоли для управления сохранениями игр и их синхронизации с облаком.

## Вклад
Мы приветствуем вклад в проект! Для этого:
1. Сделайте форк репозитория.
2. Создайте новую ветку (`git checkout -b feature-branch`).
3. Внесите изменения и закоммитьте их (`git commit -am 'Добавлена новая фича'`).
4. Сделайте push изменений (`git push origin feature-branch`).
5. Откройте pull request.

## Лицензия
Этот проект лицензируется под лицензией MIT — см. файл [LICENSE](./LICENSE.md) для подробностей.

## Контакты
Если у вас возникли вопросы или предложения, свяжитесь со мной через [GitHub Issues](https://github.com/IAMVanilka/SaveMeApp/issues/new).
