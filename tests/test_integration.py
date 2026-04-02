import time
from unittest.mock import patch
from src.core.config import ConfigManager
from src.core.events import EventSystem, Events
from src.core.key_manager import KeyManager


def test_event_system_integration():
    events = EventSystem()
    received = []

    def callback(data): received.append(data)

    events.subscribe(Events.ENTRY_ADDED, callback)
    events.publish(Events.ENTRY_ADDED, "test_data")

    assert len(received) == 1
    assert received[0] == "test_data"


def test_config_db_integration(temp_db):
    config = ConfigManager()
    config.set_db(temp_db)
    config.set("test_key", "test_value")
    config.settings.pop("test_key", None)
    val = config.get("test_key")
    assert val == "test_value"


def test_full_application_lifecycle(temp_db):
    assert temp_db.is_initialized() is False

    key_manager = KeyManager()
    password = "SuperStrongPassword123!"

    keys = key_manager.setup_new_user(password)
    temp_db.save_auth_data(keys['auth_hash'], keys['enc_salt'])

    assert temp_db.is_initialized() is True

    temp_db._temp_key = key_manager.get_session_key()
    temp_db.add_vault_entry("InitialSite", "user1", "initial_pass")

    key_manager.clear_session_key()
    assert key_manager.get_session_key() is None

    auth_data = temp_db.get_auth_data()

    assert key_manager.authenticate("WrongPass", auth_data['auth_hash'], auth_data['enc_salt']) is False

    with patch('time.time', return_value=time.time() + 2):
        assert key_manager.authenticate(password, auth_data['auth_hash'], auth_data['enc_salt']) is True

    assert key_manager.get_session_key() is not None

    temp_db._temp_key = key_manager.get_session_key()

    rows = temp_db.query("SELECT id FROM vault_entries")
    assert len(rows) == 1

    dec_pass = temp_db.get_decrypted_password(rows[0]['id'])
    assert dec_pass == "initial_pass"
