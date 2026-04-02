from abc import ABC, abstractmethod
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.core.key_manager import KeyManager

class EncryptionService(ABC):
    @abstractmethod
    def set_key_manager(self, key_manager: "KeyManager"):
        pass

    @abstractmethod
    def encrypt(self, data: bytes, key: Optional[bytes] = None) -> bytes:
        pass

    @abstractmethod
    def decrypt(self, ciphertext: bytes, key: Optional[bytes] = None) -> bytes:
        pass
