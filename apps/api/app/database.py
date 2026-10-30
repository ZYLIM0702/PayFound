from __future__ import annotations
import os
from . import config
from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./payfound_demo.db')
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql+psycopg://', 1)
if DATABASE_URL.startswith('postgresql://'):
    DATABASE_URL = DATABASE_URL.replace('postgresql://', 'postgresql+psycopg://', 1)
ARGS = {'check_same_thread': False, 'timeout': 30} if DATABASE_URL.startswith('sqlite') else {'connect_timeout': 10}
POOL = {} if DATABASE_URL.startswith('sqlite') else {'pool_size': 5, 'max_overflow': 5, 'pool_recycle': 300}
engine = create_engine(DATABASE_URL, connect_args=ARGS, pool_pre_ping=True, **POOL)
if DATABASE_URL.startswith('sqlite'):
    @event.listens_for(engine, 'connect')
    def _sqlite_pragmas(conn, rec):
        cursor = conn.cursor()
        cursor.execute('PRAGMA foreign_keys=ON')
        cursor.execute('PRAGMA busy_timeout=30000')
        cursor.close()

class Base(DeclarativeBase): pass
SessionLocal = sessionmaker(engine, autoflush=False, expire_on_commit=False)

def db_session():
    with SessionLocal() as db:
        yield db
