import os
import json
import logging
from typing import Optional, Dict, Any
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag

logger = logging.getLogger("AES256GCMService")

NONCE_SIZE = 12
TAG_SIZE = 16
VERSION = 1


class AES256GCMService:
    def __init__(self):
        self._aesgcm: Optional[AESGCM] = None
        self._key_manager = None
        self._active_key: Optional[bytes] = None

    def set_key_manager(self, key_manager):
        """ARC-2: Внедрение зависимости KeyManager."""
        self._key_manager = key_manager
        self._aesgcm = None
        self._active_key = None

    def _get_normalized_key(self) -> bytes:
        """Инициализация AESGCM с ключом из KeyManager."""
        if self._key_manager is None:
            raise RuntimeError("KeyManager not set. Call set_key_manager() first.")

        key = self._key_manager.storage.get_key()
        if key is None:
            self._aesgcm = None
            self._active_key = None
            raise RuntimeError("Encryption key not available in KeyManager.")

        if len(key) != 32:
            logger.warning(f"Key length is {len(key)}, expected 32. Truncating/padding.")
            if len(key) < 32:
                key = key.ljust(32, b'\0')
            else:
                key = key[:32]

        return key

    def _ensure_cipher(self):
        key = self._get_normalized_key()
        if self._aesgcm is None or self._active_key != key:
            self._aesgcm = AESGCM(key)
            self._active_key = key
            logger.debug("AES-256-GCM cipher initialized")

    def encrypt(self, data: bytes, associated_data: Optional[bytes] = None) -> bytes:
        self._ensure_cipher()
        nonce = os.urandom(NONCE_SIZE)
        ciphertext = self._aesgcm.encrypt(nonce, data, associated_data)
        encrypted_blob = nonce + ciphertext

        logger.debug(f"Encrypted {len(data)} bytes -> {len(encrypted_blob)} bytes")
        return encrypted_blob

    def decrypt(self, encrypted_blob: bytes, associated_data: Optional[bytes] = None) -> bytes:
        self._ensure_cipher()

        #Извлекаем nonce и ciphertext+tag
        if len(encrypted_blob) < NONCE_SIZE + TAG_SIZE:
            raise ValueError(f"Encrypted blob too short: {len(encrypted_blob)} bytes")

        nonce = encrypted_blob[:NONCE_SIZE]
        ciphertext_with_tag = encrypted_blob[NONCE_SIZE:]

        try:
            #Валидация authentication tag (происходит автоматически)
            plaintext = self._aesgcm.decrypt(nonce, ciphertext_with_tag, associated_data)
            logger.debug(f"Decrypted {len(encrypted_blob)} bytes -> {len(plaintext)} bytes")
            return plaintext
        except InvalidTag:
            logger.error("Authentication tag validation failed — possible tampering!")
            raise ValueError("Decryption failed: authentication tag invalid. Data may be tampered.")

    @staticmethod
    def encrypt_dict(data: Dict[str, Any], key_manager=None, associated_data: Optional[bytes] = None) -> bytes:
        service = AES256GCMService()
        if key_manager:
            service.set_key_manager(key_manager)

        payload = json.dumps(data, ensure_ascii=False).encode('utf-8')
        return service.encrypt(payload, associated_data)

    @staticmethod
    def decrypt_dict(encrypted_blob: bytes, key_manager=None, associated_data: Optional[bytes] = None) -> Dict[str, Any]:
        service = AES256GCMService()
        if key_manager:
            service.set_key_manager(key_manager)

        plaintext = service.decrypt(encrypted_blob, associated_data)
        return json.loads(plaintext.decode('utf-8'))
