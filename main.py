import tkinter as tk
from src.core.config import ConfigManager
from src.core.state_manager import StateManager
from src.core.events import EventSystem, Events
from src.core.key_manager import KeyManager
from src.database.db import DatabaseHelper
from src.gui.main_window import MainWindow
from src.gui.login_dialog import LoginDialog
from src.gui.setup_wizard import SetupWizard


def main():
    print(">>> Запуск CryptoSafe Manager <<<")
    config = ConfigManager(env='development')
    events = EventSystem()
    state = StateManager(events)
    key_manager = KeyManager(config)
    key_manager.state_manager = state
    db = DatabaseHelper(db_path=config.get('db_path'))
    config.set_db(db)
    root = tk.Tk()
    root.withdraw()                                 

    if db.is_initialized():
        def on_login_success(result=True):
            if result:
                app = MainWindow(root, config, state, db, events, key_manager=key_manager)
                db._temp_key = key_manager.get_session_key()
                events.publish(Events.USER_LOGGED_IN, "admin")
                app.mainloop()                      
        LoginDialog(root, db, key_manager, on_login_success)
    else:
        def on_setup_complete(password, db_path):
            if password:
                app = MainWindow(root, config, state, db, events, key_manager=key_manager)
                db._temp_key = key_manager.get_session_key()
                events.publish(Events.USER_LOGGED_IN, "admin")
                app.mainloop()
        SetupWizard(root, db, key_manager, on_setup_complete)
    root.mainloop()

if __name__ == "__main__":
    main()
