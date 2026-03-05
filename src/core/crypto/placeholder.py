from .abstract import EncryptionService

class AES256Placeholder(EncryptionService):
    """Заглушка"""
    def encrypt(self, data: bytes, key: bytes) -> bytes:
        if not key: return data
        return bytes([data[i] ^ key[i % len(key)] for i in range(len(data))])

    def decrypt(self, ciphertext: bytes, key: bytes) -> bytes:
        return self.encrypt(ciphertext, key)
