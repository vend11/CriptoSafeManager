from src.core.config import ConfigManager
from src.core.events import EventSystem, Events

def test_event_system_integration():
    events = EventSystem()
    received = []
    
    def callback(data):
        received.append(data)
    
    events.subscribe(Events.ENTRY_ADDED, callback)
    events.publish(Events.ENTRY_ADDED, "test_data")
    
    assert len(received) == 1
    assert received[0] == "test_data"

def test_config_db_integration(temp_db):
    config = ConfigManager()
    config.set_db(temp_db)
    
    # Сохраняем настройку
    config.set("test_key", "test_value")
    
    # Очищаем кэш в памяти
    config.settings.pop("test_key", None)
    
    # Читаем обратно
    val = config.get("test_key")
    assert val == "test_value"

def test_full_cycle(temp_db):
    plain_pass = "SuperSecret123"
    
    #Добавляем
    temp_db.add_vault_entry("Site", "user", plain_pass)
    
    #Проверяем расшифровку
    rows = temp_db.query("SELECT id FROM vault_entries")
    assert len(rows) == 1
    
    entry_id = rows[0]['id']
    decrypted = temp_db.get_decrypted_password(entry_id)
    
    assert decrypted == plain_pass
