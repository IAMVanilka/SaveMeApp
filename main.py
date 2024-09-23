import threading
import time
from googleapiclient.discovery import build

from scripts import auth, process_manager, console_UI, config_manager, upload_download_data

gauth = auth.google_auth()
drive = build('drive', 'v3', credentials=gauth)


if __name__ == "__main__":
    config = config_manager.read_config(upload_download_data.resource_path('settings.ini'))
    autosave = config.get("Settings", "autosave")

    if autosave == "on":
        autosave_thread = threading.Thread(target=process_manager.auto_send_saves, args=(drive,), daemon=True)
        autosave_thread.start()
    time.sleep(1)

    menu = console_UI.MainMenu()
    menu.gauth = gauth
    menu.drive = drive
    menu.run()
