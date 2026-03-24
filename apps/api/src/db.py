from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import get_settings


class Base(DeclarativeBase):
    pass


settings = get_settings()
database_url = settings.database_url
if database_url.startswith("sqlite:///./"):
    # Render/free containers can have unpredictable working dirs; keep SQLite in a writable location.
    sqlite_name = database_url.removeprefix("sqlite:///./")
    database_url = f"sqlite:////tmp/{Path(sqlite_name).name}"

connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
engine = create_engine(database_url, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
