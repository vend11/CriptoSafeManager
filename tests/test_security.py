import time
import gc
from unittest.mock import patch
from src.core.config import ConfigManager
from src.core.crypto.key_derivation import KeyDerivation
from src.core.key_manager import KeyManager


def test_argon2_parameters():
    configs = [
        {'argon2_time': 1, 'argon2_memory': 16384, 'argon2_parallelism': 1},
        {'argon2_time': 2, 'argon2_memory': 32768, 'argon2_parallelism': 2},
        {'argon2_time': 3, 'argon2_memory': 65536, 'argon2_parallelism': 4}
    ]

    for cfg in configs:
        config = ConfigManager()
        config.settings.update(cfg)
        kd = KeyDerivation(config)

        h = kd.hash_password("TestPassword123!")
        assert h.startswith('$argon2id$')
        assert kd.verify_password("TestPassword123!", h) is True


def test_key_derivation_consistency():
    kd = KeyDerivation()
    salt = kd.generate_salt()
    password = "ConsistentPassword!1"

    first_key = kd.derive_encryption_key(password, salt)

    for _ in range(99):
        current_key = kd.derive_encryption_key(password, salt)
        assert current_key == first_key, "Ключи не совпадают при одинаковых входных данных"


def test_constant_time_verification():
    kd = KeyDerivation()
    valid_hash = kd.hash_password("CorrectPassword!1")

    start = time.perf_counter()
    kd.verify_password("CorrectPassword!1", valid_hash)
    time_valid = time.perf_counter() - start

    start = time.perf_counter()
    kd.verify_password("WrongPassword!2", valid_hash)
    time_invalid = time.perf_counter() - start

    assert abs(time_valid - time_invalid) < 0.1, "Вероятна уязвимость к атаке по времени"


def test_memory_key_clearing():
    km = KeyManager()
    keys = km.setup_new_user("ClearMemoryTest!1")
    enc_key = km.get_session_key()

    assert enc_key is not None

    km.clear_session_key()
    gc.collect()

    assert km.get_session_key() is None, "Ссылка на ключ не была обнулена!"


def test_full_auth_and_crypto_cycle(temp_db):
    key_manager = KeyManager()

    keys_a = key_manager.setup_new_user("PasswordA_123!")
    temp_db.save_auth_data(keys_a['auth_hash'], keys_a['enc_salt'])
    temp_db._temp_key = key_manager.get_session_key()

    for i in range(1, 11):
        temp_db.add_vault_entry(f"Site_{i}", f"user_{i}", f"pass_{i}")

    rows_before = temp_db.query("SELECT id FROM vault_entries")
    assert len(rows_before) == 10

    old_key = key_manager.get_session_key()
    keys_b = key_manager.setup_new_user("PasswordB_456!")
    new_key = key_manager.get_session_key()

    success = temp_db.re_encrypt_all_data(old_key, new_key)
    assert success is True
    temp_db.save_auth_data(keys_b['auth_hash'], keys_b['enc_salt'])

    key_manager.clear_session_key()
    auth_data = temp_db.get_auth_data()

    with patch('time.time', return_value=time.time() + 2):
        assert key_manager.authenticate("PasswordB_456!", auth_data['auth_hash'], auth_data['enc_salt']) is True

    temp_db._temp_key = key_manager.get_session_key()

    for i in range(1, 11):
        row = temp_db.query("SELECT id FROM vault_entries WHERE title=?", (f"Site_{i}",))[0]
        decrypted = temp_db.get_decrypted_password(row['id'])
        assert decrypted == f"pass_{i}", f"Ошибка расшифровки записи {i} после смены пароля"
