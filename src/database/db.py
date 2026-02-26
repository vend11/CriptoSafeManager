import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

engine = create_engine("sqlite:///cryptosafe.db", connect_args={"check_same_thread": False})
Session = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(engine)
    conn = sqlite3.connect("cryptosafe.db")
    conn.execute("PRAGMA user_version = 1")
    conn.close()

def backup_placeholder():
    print("Заглушка резервного копирования")
