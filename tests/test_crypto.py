from src.core.crypto.placeholder import AES256Placeholder
from src.core.key_manager import KeyManager


def test_xor_encryption():
    crypto = AES256Placeholder()
    key = b'test_key_16bytes'
    data = b'sensitive_data'

    encrypted = crypto.encrypt(data, key)
    assert encrypted != data

    decrypted = crypto.decrypt(encrypted, key)
    assert decrypted == data


def test_key_derivation():
    km = KeyManager()
    salt = km.generate_salt()

    assert len(salt) == 16
    assert isinstance(salt, bytes)

    key1 = km.derive_key("password", salt)
    key2 = km.derive_key("password", salt)

    assert key1 == key2
    assert len(key1) == 32 
