import ctypes
from .abstract import EncryptionService


class AES256Placeholder(EncryptionService):
    def encrypt(self, data: bytes, key: bytes) -> bytes:
        result = bytes([b ^ key[i % len(key)] for i, b in enumerate(data)])
        self._wipe(data)
        return result

    def decrypt(self, ciphertext: bytes, key: bytes) -> bytes:
        return self.encrypt(ciphertext, key)

    def _wipe(self, data: bytes):
        if data:
            location = id(data) + 20
            ctypes.memset(location, 0, len(data))
