import ctypes
import time
from typing import Optional

class KeyStorage:
    def __init__(self):
        self._session_key: Optional[bytearray] = None
        self._last_activity: float = 0
        self._timeout: int = 3600

    def store_key(self, key: bytes):
        self.clear_key()
        self._session_key = bytearray(key)
        self.update_activity()

    def get_key(self) -> Optional[bytes]:
        if self._session_key and (time.time() - self._last_activity < self._timeout):
            return bytes(self._session_key)
        self.clear_key()
        return None

    def update_activity(self):
        self._last_activity = time.time()

    def clear_key(self):
        if self._session_key and isinstance(self._session_key, bytearray):
            try:
                buf = (ctypes.c_char * len(self._session_key)).from_buffer(self._session_key)
                ctypes.memset(buf, 0, len(self._session_key))
            except Exception:
                for i in range(len(self._session_key)):
                    self._session_key[i] = 0
        self._session_key = None
