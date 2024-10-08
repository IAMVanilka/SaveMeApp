# MIT License
#
# Copyright (c) 2024 IAMVanilka
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import threading
import time
from googleapiclient.discovery import build

from scripts import auth, process_manager, console_UI, config_manager, upload_download_data

gauth = auth.google_auth()
drive = build('drive', 'v3', credentials=gauth)

if __name__ == "__main__":
    config = config_manager.read_config(upload_download_data.resource_path('settings.ini'))
    autosave = config.get("Settings", "autosave")

    # Запуск автосохранения в отдельном потоке
    if autosave == "on":
        autosave_thread = threading.Thread(target=process_manager.auto_send_saves, args=(drive,), daemon=True)
        autosave_thread.start()

    time.sleep(1)

    # Основной поток программы - меню
    menu = console_UI.MainMenu()
    menu.gauth = gauth
    menu.drive = drive
    menu.run()
