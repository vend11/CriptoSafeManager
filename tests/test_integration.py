from src.core.config import ConfigManager
from src.core.events import Events


def test_event_system_integration(event_system):
    received = []

    def callback(data):
        received.append(data)

    event_system.subscribe(Events.ENTRY_ADDED, callback)
    event_system.publish(Events.ENTRY_ADDED, "test_data")

    assert len(received) == 1
    assert received[0] == "test_data"


def test_config_db_integration(temp_db): #сохранение настроек в БД
    config = ConfigManager()
    config.set_db(temp_db)
    #сохраняем настройку
    config.set("test_key", "test_value")
    #очищаем кэш в памяти, чтобы проверить чтение из БД
    config.settings.pop("test_key", None)
    #читаем обратно
    val = config.get("test_key")
    assert val == "test_value"


def test_full_workflow(temp_db, event_system):
    #добавляем запись
    temp_db.add_vault_entry("Site", "user", "pass123")
    #проверяем, что записалась
    rows = temp_db.fetch_all("SELECT * FROM vault_entries")
    assert len(rows) == 1
    #проверяем расшифровку
    decrypted = temp_db.get_decrypted_password(rows[0]['id'])
    assert decrypted == "pass123"
