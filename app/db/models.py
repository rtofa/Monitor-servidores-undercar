from sqlalchemy import Boolean, Column, Float, Integer, String, DateTime
from datetime import datetime
from app.db.database import Base

class ServerState(Base):
    __tablename__ = "server_states"

    id = Column(Integer, primary_key=True, index=True)
    server_name = Column(String, unique=True, index=True)
    status = Column(String, default="ONLINE")  # 'ONLINE' como default 
    last_checked = Column(DateTime, default=datetime.utcnow)
    status_changed_at = Column(DateTime, default=datetime.utcnow)
    cpu_usage = Column(Float, nullable=True) 
    ram_usage = Column(Float, nullable=True)
    gpu_usage = Column(Float, nullable=True)

class ServerEvent(Base):
    __tablename__ = "server_events"
    
    id = Column(Integer, primary_key=True, index=True)
    server_name = Column(String, index=True)
    event_type = Column(String) # Ex: "OFFLINE", "ONLINE", "WARNING"
    message = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)