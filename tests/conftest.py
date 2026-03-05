import pytest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.db import DatabaseHelper
from src.core.events import EventSystem

@pytest.fixture
def temp_db(tmp_path):
    """
    Фикстура тестовой базы данных.
    Создает временную БД для каждого теста.
    """
    db_file = tmp_path / "test_cryptosafe.db"
    db = DatabaseHelper(str(db_file))
    return db

@pytest.fixture
def event_system():
    return EventSystem()
