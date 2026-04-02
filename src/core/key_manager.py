from typing import Optional, Dict
from src.core.crypto.key_derivation import KeyDerivation
from src.core.crypto.key_storage import KeyStorage
from src.core.crypto.authentication import AuthenticationService


class KeyManager:
    def __init__(self, config=None):
        self.storage = KeyStorage()
        self.derivation = KeyDerivation(config)
        self.auth = AuthenticationService(self.storage, self.derivation)

    def setup_new_user(self, password: str) -> dict:
        auth_hash = self.derivation.hash_password(password)
        enc_salt = self.derivation.generate_salt()
        audit_salt = self.derivation.generate_salt()
        export_salt = self.derivation.generate_salt()

        enc_key = self.derivation.derive_encryption_key(password, enc_salt)
        self.storage.store_key(enc_key)

        return {
            "auth_hash": auth_hash,
            "enc_salt": enc_salt,
            "audit_salt": audit_salt,
            "export_salt": export_salt
        }

    def authenticate(self, password: str, auth_hash: str, enc_salt: bytes, mfa_code: str = None) -> bool:
        return self.auth.login(password, auth_hash, enc_salt, mfa_code)

    def get_session_key(self) -> Optional[bytes]:
        return self.storage.get_key()

    def clear_session_key(self):
        self.storage.clear_key()

    def get_remaining_lock_time(self) -> float:
        return self.auth.get_remaining_lock_time()
