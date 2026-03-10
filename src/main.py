import tkinter as tk
from src.core.config import ConfigManager
from src.core.state_manager import StateManager
from src.core.events import EventSystem
from src.database.db import DatabaseHelper
from src.gui.main_window import MainWindow


def main():
    print(" Запуск CryptoSafe Manager ")

    # 1. Инициализация ядра
    config = ConfigManager(env='development')
    events = EventSystem()

    state = StateManager(events)

    # 2. База данных
    db = DatabaseHelper(db_path=config.get('db_path'))

    # 3. Связка Config <-> DB
    config.set_db(db)

    # 4. Запуск GUI
    app = MainWindow(config, state, db, events)
    app.mainloop()


if __name__ == "__main__":
    main()
