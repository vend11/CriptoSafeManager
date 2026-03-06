import sqlite3
import shutil
import os
import secrets
import base64
from datetime import datetime
from pathlib import Path
from queue import Queue, Empty
from contextlib import contextmanager
from typing import Callable, List, Optional
from .models import SCHEMA_V1
from src.core.crypto.placeholder import AES256Placeholder


class DatabasePool:
    def __init__(self, db_path: str, size: int = 4):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.size = max(1, size)
        self._pool: "Queue[sqlite3.Connection]" = Queue(maxsize=self.size)
        self._fill_pool()
        self.crypto = AES256Placeholder()
        self._temp_key = secrets.token_bytes(16)

        self._migrations: List[Callable[[sqlite3.Connection], None]] = [
            self._migration_1_initial_schema,
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
                try:
                    conn.close()
                except Exception:
                    pass
            else:
                try:
                    self._pool.put_nowait(conn)
                except Exception:
                    try:
                        conn.close()
                    except Exception:
                        pass

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

    def get_user_version(self) -> int:
        with self.connection() as conn:
            cur = conn.cursor()
            cur.execute('PRAGMA user_version')
            row = cur.fetchone()
            return int(row[0]) if row is not None else 0

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
        print("[DB] Миграция V1 применена (Схема загружена)")

    def add_vault_entry(self, title: str, username: str, password_str: str, url: str = ""):
        encrypted_bytes = self.crypto.encrypt(password_str.encode('utf-8'), self._temp_key)
        encrypted_str = base64.b64encode(encrypted_bytes).decode('utf-8')

        query = "INSERT INTO vault_entries (title, username, encrypted_password, url) VALUES (?, ?, ?, ?)"
        self.execute(query, (title, username, encrypted_str, url), commit=True)
        print(f"[DB] Запись '{title}' добавлена.")

    def delete_entry(self, entry_id: int):
        query = "DELETE FROM vault_entries WHERE id = ?"
        self.execute(query, (entry_id,), commit=True)
        print(f"[DB] Запись ID {entry_id} удалена.")

    def get_decrypted_password(self, entry_id: int) -> Optional[str]:
        rows = self.query("SELECT encrypted_password FROM vault_entries WHERE id=?", (entry_id,))
        if rows:
            encrypted_str = rows[0]['encrypted_password']
            try:
                encrypted_bytes = base64.b64decode(encrypted_str)
                decrypted_bytes = self.crypto.decrypt(encrypted_bytes, self._temp_key)
                return decrypted_bytes.decode('utf-8')
            except Exception as e:
                print(f"[DB ERROR] Ошибка расшифровки: {e}")
                return None
        return None

    def create_backup(self, backup_dir: str = 'backups') -> Optional[str]:
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(backup_dir, f"backup_{timestamp}.db")

        try:
            shutil.copy2(self.db_path, backup_path)
            print(f"[DB] Бэкап создан: {backup_path}")
            return backup_path
        except Exception as e:
            print(f"[DB ERROR] Ошибка бэкапа: {e}")
            return None
