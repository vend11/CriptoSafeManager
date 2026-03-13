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

        self.settings['clipboard_timeout'] = 30
        self.settings['auto_lock_timeout'] = 300

    def set_db(self, database: "DatabaseHelper"):
        self.db = database

    def get(self, key, default=None):
        if key in self.settings:
            return self.settings[key]

        if self.db:
            try:
                rows = self.db.query("SELECT setting_value FROM settings WHERE setting_key=?", (key,))
                if rows:
                    return rows[0][0]
            except Exception as e:
                print(f"[CONFIG] Ошибка чтения ключа {key}: {e}")

        return default

    def set(self, key, value, encrypted=False):
        self.settings[key] = value

        if self.db:
            self.db.execute(
                "INSERT OR REPLACE INTO settings (setting_key, setting_value, encrypted) VALUES (?, ?, ?)",
                (key, str(value), 1 if encrypted else 0),
                commit=True
            )
