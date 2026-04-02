import time
from .key_derivation import KeyDerivation
from .key_storage import KeyStorage


class AuthenticationService:
    def __init__(self, storage: KeyStorage, derivation: KeyDerivation):
        self.storage = storage
        self.derivation = derivation
        self._failed_attempts = 0
        self._lock_until = 0

    def login(self, password: str, auth_hash: str, enc_salt: bytes, mfa_code: str = None) -> bool:
        if time.time() < self._lock_until:
            return False

        if self.derivation.verify_password(password, auth_hash):
            enc_key = self.derivation.derive_encryption_key(password, enc_salt)
            self.storage.store_key(enc_key)
            self._failed_attempts = 0
            return True

        self._failed_attempts += 1
        delay = 0
        if 1 <= self._failed_attempts <= 2:
            delay = 1
        elif 3 <= self._failed_attempts <= 4:
            delay = 5
        else:
            delay = 30

        if delay > 0:
            self._lock_until = time.time() + delay
        return False

    def get_remaining_lock_time(self) -> float:
        remaining = self._lock_until - time.time()
        return max(0.0, remaining)
