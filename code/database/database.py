from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

URL_DATABASE = os.getenv("URL_DATABASE")

Engine = None
SessionLocal = None
Base = None

def set_database_engine():
    """Set the database engine, session and base."""
    global Engine, SessionLocal, Base
    Engine = create_engine(URL_DATABASE)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=Engine)
    Base = declarative_base()
    print(f"Set database engine to: {Engine}")
    # print(f"Set database session to: {SessionLocal}")
    # print(f"Set database base to: {Base}")

set_database_engine()

def get_db():
    """Get db dependency, don't touch!
    This makes a new database session for the request and closes it after the request is done.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()