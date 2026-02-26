from sqlalchemy import Column, Integer, String, LargeBinary, DateTime, Boolean
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class VaultEntry(Base):
    __tablename__ = 'vault_entries'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    username = Column(String)
    encrypted_password = Column(LargeBinary, nullable=False)
    url = Column(String)
    notes = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

# Таблицы для будущих спринтов
class AuditLog(Base): __tablename__ = 'audit_log'; id = Column(Integer, primary_key=True); action = Column(String)
class Setting(Base): __tablename__ = 'settings'; id = Column(Integer, primary_key=True); setting_key = Column(String)
class KeyStore(Base): __tablename__ = 'key_store'; id = Column(Integer, primary_key=True); key_type = Column(String)
