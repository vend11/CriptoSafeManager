import os

def test_tables_creation(temp_db):
    result = temp_db.query("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row['name'] for row in result}
    
    assert 'vault_entries' in tables
    assert 'settings' in tables
    assert 'key_store' in tables

def test_migration_version(temp_db):
    """TEST-1: Проверка работы миграций (DB-3)."""
    rows = temp_db.query("PRAGMA user_version")
    assert rows[0][0] == 1

def test_encryption_is_base64(temp_db):
    plain_password = "my_secret_pass"
    temp_db.add_vault_entry("TestSite", "user", plain_password, "http://test.com")
    
    # Читаем сырые данные из БД
    rows = temp_db.query("SELECT encrypted_password FROM vault_entries WHERE title='TestSite'")
    assert len(rows) == 1
    
    stored_value = rows[0]['encrypted_password']
    
    #Проверяем, что это строка
    assert isinstance(stored_value, str)
    
    #проверяем, что это не открытый пароль
    assert stored_value != plain_password
    
    #Проверяем, что строка похожа на Base64
    import base64
    try:
        decoded = base64.b64decode(stored_value)
        # Если декодировалось, значит это валидный Base64
        assert len(decoded) > 0
    except Exception:
        assert False, "Данные в базе не являются валидной строкой Base64"

def test_backup_stub(temp_db):
    result = temp_db.create_backup()
    assert result is not None
