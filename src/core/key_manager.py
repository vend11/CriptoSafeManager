import hashlib
import secrets
import ctypes
from typing import Optional


class KeyManager:
    _key_storage = {}

    def derive_key(self, password: str, salt: bytes) -> bytes:
        if not password or not salt:
            raise ValueError("Пароль и соль не могут быть пустыми")

        # заглушка
        return hashlib.sha256(salt + password.encode('utf-8')).digest()

    def generate_salt(self) -> bytes:
        """Генерация случайной соли."""
        return secrets.token_bytes(16)

    def store_key(self, key: bytes, key_id: str = "master") -> bool:
        if not isinstance(key, bytes):
            raise TypeError("Ключ должен быть байтами")

        self._key_storage[key_id] = key
        print(f"[KEY_MGR] Ключ '{key_id}' сохранен в ОЗУ (заглушка)")
        return True

    def load_key(self, key_id: str = "master") -> Optional[bytes]:
        key = self._key_storage.get(key_id)
        if key:
            print(f"[KEY_MGR] Ключ '{key_id}' загружен из ОЗУ (заглушка)")
        else:
            print(f"[KEY_MGR] Ключ '{key_id}' не найден")
        return key

    @staticmethod
    def secure_clear(data):
        if data is None:
            return

        if isinstance(data, (bytes, bytearray)):
            # Создаем буфер для записи нулей
            buffer = (ctypes.c_char * len(data)).from_address(id(data))
            ctypes.memset(buffer, 0, len(data))
            print("[KEY_MGR] Память очищена (secure_clear)")
        elif isinstance(data, str):
            try:
                ctypes.memset(id(data) + 32, 0, len(data) * 2)
            except Exception:
                pass  
