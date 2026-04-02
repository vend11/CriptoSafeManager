import os
import base64


def test_tables_creation(temp_db):
    result = temp_db.query("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row['name'] for row in result}

    assert 'vault_entries' in tables
    assert 'settings' in tables
    assert 'key_store' in tables

def test_migration_version(temp_db):
    rows = temp_db.query("PRAGMA user_version")
    assert rows[0][0] == 3

def test_key_store_structure(temp_db):
    cols = temp_db.query("PRAGMA table_info(key_store)")
    col_names = {row['name'] for row in cols}

    assert 'key_type' in col_names
    assert 'key_data' in col_names
    assert 'version' in col_names
    assert 'created_at' in col_names

def test_encryption_is_base64(temp_db):
    temp_db.add_vault_entry("TestSite", "user", "my_secret_pass", "http://test.com")
    rows = temp_db.query("SELECT encrypted_password FROM vault_entries WHERE title='TestSite'")
    assert len(rows) == 1
    stored_value = rows[0]['encrypted_password']
    assert isinstance(stored_value, str)
    assert stored_value != "my_secret_pass"

    try:
        decoded = base64.b64decode(stored_value)
        assert len(decoded) > 0
    except Exception:
        assert False, "Данные не являются валидной строкой Base64"


def test_default_settings_exist(temp_db):
    rows = temp_db.query("SELECT setting_value FROM settings WHERE setting_key='auto_lock_timeout'")
    assert len(rows) == 1
    assert rows[0][0] == '300'
