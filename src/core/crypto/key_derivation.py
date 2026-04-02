import os
import secrets
from typing import Tuple
from argon2 import PasswordHasher, Type
from argon2.exceptions import VerifyMismatchError
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend


class KeyDerivation:
    MAX_TIME_COST = 10
    MAX_MEMORY_COST = 262144
    MAX_PARALLELISM = 16

    def __init__(self, config=None):
        time_cost = 3
        memory_cost = 65536
        parallelism = 4

        if config:
            try:
                time_cost = int(config.get('argon2_time', 3))
                memory_cost = int(config.get('argon2_memory', 65536))
                parallelism = int(config.get('argon2_parallelism', 4))
            except ValueError:
                pass

        time_cost = min(max(time_cost, 1), self.MAX_TIME_COST)
        memory_cost = min(max(memory_cost, 1024), self.MAX_MEMORY_COST)
        parallelism = min(max(parallelism, 1), self.MAX_PARALLELISM)

        self.ph = PasswordHasher(
            time_cost=time_cost,
            memory_cost=memory_cost,
            parallelism=parallelism,
            hash_len=32,
            salt_len=16,
            type=Type.ID
        )
        self.pbkdf2_iterations = 100000

    def hash_password(self, password: str) -> str:
        return self.ph.hash(password)

    def verify_password(self, password: str, stored_hash: str) -> bool:
        try:
            return self.ph.verify(stored_hash, password)
        except VerifyMismatchError:
            secrets.compare_digest(b'dummy', b'dummy')
            return False
        except Exception:
            return False

    def generate_salt(self, length: int = 16) -> bytes:
        return os.urandom(length)

    def derive_encryption_key(self, password: str, salt: bytes) -> bytearray:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=self.pbkdf2_iterations,
            backend=default_backend()
        )
        return bytearray(kdf.derive(password.encode('utf-8')))

    def derive_audit_key(self, password: str, salt: bytes) -> bytearray:
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=self.pbkdf2_iterations,
                         backend=default_backend())
        return bytearray(kdf.derive((password + "_audit").encode('utf-8')))
