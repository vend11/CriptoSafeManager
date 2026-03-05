import os


def test_tables_creation(temp_db):
    result = temp_db.fetch_all("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row['name'] for row in result}

    assert 'vault_entries' in tables
    assert 'audit_log' in tables
    assert 'settings' in tables
    assert 'key_store' in tables


def test_migration_version(temp_db):
    rows = temp_db.fetch_all("PRAGMA user_version")
    assert rows[0][0] == 1


def test_encryption_before_insert(temp_db):

    plain_password = "my_secret_pass"
    temp_db.add_vault_entry("TestSite", "user", plain_password, "http://test.com")

    rows = temp_db.fetch_all("SELECT encrypted_password FROM vault_entries WHERE title='TestSite'")
    assert len(rows) == 1

    stored_value = rows[0]['encrypted_password']

    assert stored_value != plain_password.encode()
    assert stored_value != plain_password

    assert isinstance(stored_value, bytes)


def test_backup_mechanism(temp_db):

    temp_db.add_vault_entry("BackupTest", "user", "pass", "url")

    # Создаем бэкап
    backup_file = temp_db.create_backup()

    assert backup_file is not None
    assert os.path.exists(backup_file)
    assert os.path.getsize(backup_file) > 0
