import sqlite3
import secrets
import base64
import time
from pathlib import Path
from queue import Queue, Empty
from contextlib import contextmanager
from typing import Callable, List, Optional
from .models import SCHEMA_V1, SCHEMA_V3_UPDATE
from src.core.crypto.placeholder import AES256Placeholder


class DatabaseHelper:
    def __init__(self, db_path: str, size: int = 4):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.size = max(1, size)
        self._pool: "Queue[sqlite3.Connection]" = Queue(maxsize=self.size)
        self._fill_pool()
        self.crypto = AES256Placeholder()
        self._temp_key = secrets.token_bytes(16)
        self._migrations = [self._migration_1_initial_schema, self._migration_2_ensure_settings,
                            self._migration_3_update_key_store]
        self.migrate()

    def _new_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _fill_pool(self) -> None:
        for _ in range(self.size): self._pool.put(self._new_connection())

    @contextmanager
    def connection(self):
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

    def execute(self, sql, params=(), commit=False):
        with self.connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, params)
            if commit: conn.commit()
            return cur

    def query(self, sql, params=()):
        return self.execute(sql, params).fetchall()

    def fetch_all(self, sql, params=()):
        return self.query(sql, params)

    def get_user_version(self):
        with self.connection() as conn:
            r = conn.execute('PRAGMA user_version').fetchone()
            return int(r[0]) if r else 0

    def _set_user_version(self, v):
        with self.connection() as conn:
            conn.execute(f'PRAGMA user_version = {int(v)}');
            conn.commit()

    def migrate(self):
        curr = self.get_user_version()
        if curr >= len(self._migrations): return
        for i in range(curr, len(self._migrations)):
            with self.connection() as conn:
                self._migrations[i](conn)
                self._set_user_version(i + 1)

    def _migration_1_initial_schema(self, conn):
        conn.executescript(SCHEMA_V1);
        conn.commit()

    def _migration_2_ensure_settings(self, conn):
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
            ('auto_lock_timeout', '300'),
            ('argon2_time', '3'),
            ('argon2_memory', '65536'),
            ('argon2_parallelism', '4')
        ]
        cur.executemany(
            "INSERT OR IGNORE INTO settings (setting_key, setting_value) VALUES (?, ?)",
            default_settings
        )
        conn.commit()

    def _migration_3_update_key_store(self, conn):
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='key_store'")
        if cur.fetchone():
            cur.executescript(SCHEMA_V3_UPDATE)
        else:
            cur.executescript("""
                CREATE TABLE key_store (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key_type TEXT NOT NULL,
                    key_data BLOB,
                    version INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
             """)
        conn.commit()

    def is_initialized(self):
        return len(self.query("SELECT id FROM key_store WHERE key_type='auth_hash'")) > 0

    def save_auth_data(self, auth_hash: str, enc_salt: bytes, audit_salt: bytes = None, export_salt: bytes = None):
        self.execute("DELETE FROM key_store", commit=True)
        self.execute("INSERT INTO key_store (key_type, key_data) VALUES (?, ?)",
                     ("auth_hash", auth_hash.encode('utf-8')), commit=True)
        self.execute("INSERT INTO key_store (key_type, key_data) VALUES (?, ?)", ("enc_salt", enc_salt), commit=True)
        if audit_salt: self.execute("INSERT INTO key_store (key_type, key_data) VALUES (?, ?)",
                                    ("audit_salt", audit_salt), commit=True)
        if export_salt: self.execute("INSERT INTO key_store (key_type, key_data) VALUES (?, ?)",
                                     ("export_salt", export_salt), commit=True)

    def get_auth_data(self):
        rows = self.query("SELECT key_type, key_data FROM key_store")
        data = {}
        for r in rows:
            if r['key_type'] == 'auth_hash':
                data['auth_hash'] = r['key_data'].decode('utf-8')
            elif r['key_type'] == 'enc_salt':
                data['enc_salt'] = r['key_data']
        return data

    def re_encrypt_all_data(self, old_key: bytes, new_key: bytes, progress_cb=None) -> bool:
        conn = None
        try:
            conn = self._new_connection()
            cur = conn.cursor()
            cur.execute("BEGIN TRANSACTION")
            cur.execute("SELECT id, encrypted_password FROM vault_entries")
            rows = cur.fetchall()
            for i, r in enumerate(rows):
                old_b = base64.b64decode(r['encrypted_password'])
                dec = self.crypto.decrypt(old_b, old_key)
                new_b = self.crypto.encrypt(dec, new_key)
                cur.execute("UPDATE vault_entries SET encrypted_password = ? WHERE id = ?",
                            (base64.b64encode(new_b).decode(), r['id']))
                if progress_cb: progress_cb((i + 1) / len(rows) * 100)
            conn.commit()
            return True
        except Exception as e:
            print(f"Re-encrypt error: {e}")
            if conn: conn.rollback()
            return False
        finally:
            if conn: conn.close()

    def add_vault_entry(self, t, u, p, url=""):
        enc = base64.b64encode(self.crypto.encrypt(p.encode(), self._temp_key)).decode()
        self.execute("INSERT INTO vault_entries (title, username, encrypted_password, url) VALUES (?,?,?,?)",
                     (t, u, enc, url), True)

    def delete_entry(self, eid):
        self.execute("DELETE FROM vault_entries WHERE id=?", (eid,), True)

    def get_decrypted_password(self, eid):
        r = self.query("SELECT encrypted_password FROM vault_entries WHERE id=?", (eid,))
        if r: return self.crypto.decrypt(base64.b64decode(r[0]['encrypted_password']), self._temp_key).decode()

    def create_backup(self):
        return "stub.db"
