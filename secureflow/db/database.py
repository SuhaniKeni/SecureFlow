import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from secureflow.db.models import Base

DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "secureflow.db")
DATABASE_URL = os.environ.get("SECUREFLOW_DB_URL", f"sqlite:///{DEFAULT_DB_PATH}")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db(db_engine=None):
    """Initializes the database schema by creating all tables."""
    target_engine = db_engine or engine
    Base.metadata.create_all(bind=target_engine)

def get_db_session() -> Session:
    """Yields a database session."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
