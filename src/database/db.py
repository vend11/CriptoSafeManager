import sqlite3
import threading
import shutil
import os
from datetime import datetime
from .models import SCHEMA_V1
from src.core.crypto.placeholder import AES256Placeholder


class DatabaseHelper:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, db_path='cryptosafe.db'):
        if hasattr(self, '_initialized'):
            return

        self.db_path = db_path
        #заглушка шифрования
        self.crypto = AES256Placeholder()
        self._temp_key = b'student_key_1234'

        self._init_db()
        self._initialized = True

    def _get_connection(self): #потоко безоп
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("PRAGMA user_version")
        version = cursor.fetchone()[0]

        if version == 0:
            cursor.executescript(SCHEMA_V1)
            cursor.execute("PRAGMA user_version = 1")
            conn.commit()
            print("[DB] База создана (Версия 1)")

        conn.close()

    def execute(self, query, params=(), commit=True):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            if commit:
                conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"[DB ERROR] {e}")
        finally:
            conn.close()
        return None

    def fetch_all(self, query, params=()):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            # Возвращаем список словарей
            return [dict(r) for r in cursor.fetchall()]
        finally:
            conn.close()
    def add_vault_entry(self, title, username, password_str, url=""): # шифр пароля перед вставкой
        pass_bytes = password_str.encode('utf-8')
        encrypted_pass = self.crypto.encrypt(pass_bytes, self._temp_key)

        query = "INSERT INTO vault_entries (title, username, encrypted_password, url) VALUES (?, ?, ?, ?)"
        self.execute(query, (title, username, encrypted_pass, url))
        print(f"[DB] Запись '{title}' сохранена (пароль зашифрован)")

    def get_decrypted_password(self, entry_id):
        rows = self.fetch_all("SELECT encrypted_password FROM vault_entries WHERE id=?", (entry_id,))
        if rows:
            enc = rows[0]['encrypted_password']
            return self.crypto.decrypt(enc, self._temp_key).decode('utf-8')
        return None

    def create_backup(self, backup_dir='backups'): #заглушка
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(backup_dir, f"backup_{timestamp}.db")

        try:
            shutil.copy2(self.db_path, backup_path)
            print(f"[DB] Бэкап готов: {backup_path}")
            return backup_path
        except Exception as e:
            print(f"[DB ERROR] Ошибка бэкапа: {e}")
            return None
