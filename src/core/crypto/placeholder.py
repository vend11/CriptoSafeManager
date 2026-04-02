from .abstract import EncryptionService
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from src.core.key_manager import KeyManager


class AES256Placeholder(EncryptionService):
    def __init__(self):
        self._key_manager = None

    def set_key_manager(self, key_manager: "KeyManager"):
        self._key_manager = key_manager

    def encrypt(self, data: bytes, key: Optional[bytes] = None) -> bytes:
        target_key = key
        if target_key is None:
            if not self._key_manager:
                raise RuntimeError("KeyManager not set and no key provided")
            target_key = self._key_manager.get_session_key()

        if not target_key:
            raise RuntimeError("Encryption key is missing")

        return bytes([data[i] ^ target_key[i % len(target_key)] for i in range(len(data))])

    def decrypt(self, ciphertext: bytes, key: Optional[bytes] = None) -> bytes:
        return self.encrypt(ciphertext, key)
