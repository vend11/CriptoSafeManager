import sqlite3
import secrets
import base64
from pathlib import Path
from queue import Queue, Empty
from contextlib import contextmanager
from typing import Callable, List, Optional
from .models import SCHEMA_V1
from src.core.crypto.placeholder import AES256Placeholder


class DatabaseHelper:
    def __init__(self, db_path: str, size: int = 4):
        # Путь к файлу БД
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Пул соединений
        self.size = max(1, size)
        self._pool: "Queue[sqlite3.Connection]" = Queue(maxsize=self.size)
        self._fill_pool()

        # Криптография
        self.crypto = AES256Placeholder()
        self._temp_key = secrets.token_bytes(16)

        # Миграции (добавлена вторая миграция для надежности)
        self._migrations: List[Callable[[sqlite3.Connection], None]] = [
            self._migration_1_initial_schema,
            self._migration_2_ensure_settings,
        ]
        self.migrate()

    def _new_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _fill_pool(self) -> None:
        for _ in range(self.size):
            self._pool.put(self._new_connection())

    @contextmanager
    def connection(self) -> sqlite3.Connection:
        try:
            conn = self._pool.get_nowait()
            temporary = False
        except Empty:
            conn = self._new_connection()
            temporary = True

        try:
            yield conn
        finally:
            if temporary:
                conn.close()
            else:
                self._pool.put_nowait(conn)

    def execute(self, sql: str, params: tuple = (), commit: bool = False) -> sqlite3.Cursor:
        with self.connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, params)
            if commit:
                conn.commit()
            return cur

    def query(self, sql: str, params: tuple = ()) -> list:
        cur = self.execute(sql, params)
        return cur.fetchall()

    def fetch_all(self, sql: str, params: tuple = ()) -> list:
        return self.query(sql, params)

    def get_user_version(self) -> int:
        with self.connection() as conn:
            cur = conn.cursor()
            cur.execute('PRAGMA user_version')
            row = cur.fetchone()
            return int(row[0]) if row else 0

    def _set_user_version(self, v: int) -> None:
        with self.connection() as conn:
            cur = conn.cursor()
            cur.execute(f'PRAGMA user_version = {int(v)}')
            conn.commit()

    def migrate(self) -> None:
        current = self.get_user_version()
        target = len(self._migrations)
        if current >= target:
            return

        for idx in range(current, target):
            migration = self._migrations[idx]
            with self.connection() as conn:
                migration(conn)
                self._set_user_version(idx + 1)

    def _migration_1_initial_schema(self, conn: sqlite3.Connection) -> None:
        cur = conn.cursor()
        cur.executescript(SCHEMA_V1)
        conn.commit()
        print("[DB] Миграция V1 применена")

    def _migration_2_ensure_settings(self, conn: sqlite3.Connection) -> None:
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    setting_key TEXT UNIQUE NOT NULL,
                    setting_value TEXT,
                    encrypted INTEGER DEFAULT 0
                );
            """)
            default_settings = [
                ('clipboard_timeout', '30'),
                ('auto_lock_timeout', '300')
            ]
            cur.executemany(
                "INSERT OR IGNORE INTO settings (setting_key, setting_value) VALUES (?, ?)",
                default_settings
            )
            conn.commit()
            print("[DB] Миграция V2: Таблица настроек проверена, значения по умолчанию добавлены")

    def get_setting(self, key: str, default: str = None) -> Optional[str]:
            rows = self.query("SELECT setting_value FROM settings WHERE setting_key=?", (key,))
            return rows[0]['setting_value'] if rows else default

    def add_vault_entry(self, title: str, username: str, password_str: str, url: str = ""):
        # Шифруем и кодируем в Base64
        encrypted_bytes = self.crypto.encrypt(password_str.encode('utf-8'), self._temp_key)
        encrypted_str = base64.b64encode(encrypted_bytes).decode('utf-8')

        query = "INSERT INTO vault_entries (title, username, encrypted_password, url) VALUES (?, ?, ?, ?)"
        self.execute(query, (title, username, encrypted_str, url), commit=True)
        print(f"[DB] Запись '{title}' добавлена.")

    def delete_entry(self, entry_id: int):
        self.execute("DELETE FROM vault_entries WHERE id = ?", (entry_id,), commit=True)
        print(f"[DB] Запись ID {entry_id} удалена.")

    def get_decrypted_password(self, entry_id: int) -> Optional[str]:
        rows = self.query("SELECT encrypted_password FROM vault_entries WHERE id=?", (entry_id,))
        if rows:
            encrypted_str = rows[0]['encrypted_password']
            try:
                # Декодируем Base64 и расшифровываем
                encrypted_bytes = base64.b64decode(encrypted_str)
                decrypted_bytes = self.crypto.decrypt(encrypted_bytes, self._temp_key)
                return decrypted_bytes.decode('utf-8')
            except Exception:
                return None
        return None

    def create_backup(self, backup_dir: str = 'backups') -> Optional[str]:
        print("[DB] Создание бэкапа... (Заглушка)")
        return "stub_backup.db"

    def restore_backup(self, backup_path: str) -> bool:
        print(f"[DB] Восстановление из {backup_path}... (Заглушка)")
        return True
