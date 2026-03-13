from typing import Optional, TYPE_CHECKING
if TYPE_CHECKING:
    from src.database.db import DatabaseHelper

class ConfigManager:
    def __init__(self, env='development'):
        self.env = env
        self.db: Optional["DatabaseHelper"] = None
        self.settings = {}

        if self.env == 'development':
            self.settings['db_path'] = 'dev_cryptosafe.db'
        else:
            self.settings['db_path'] = 'cryptosafe.db'

    def set_db(self, database: "DatabaseHelper"):
        self.db = database

    def get(self, key, default=None):
        if key in self.settings:
            return self.settings[key]

        if self.db:
            try:
                val = self.db.get_setting(key)
                if val is not None:
                    return int(val) if val.isdigit() else val
            except Exception as e:
                print(f"[CONFIG] Ошибка чтения ключа {key}: {e}")

        return default
