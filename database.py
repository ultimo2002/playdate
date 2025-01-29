from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from config import DB_CONFIG, load_env

URL_DATABASE = 'postgresql://user:password@localhost:5432/database'

Engine = None
SessionLocal = None
Base = None

def set_database_url():
    """Set the database URL based on the environment variables."""
    load_env() # load the environment variables from the .env file

    global URL_DATABASE
    URL_DATABASE = f"postgresql://{DB_CONFIG['DB_USER']}:{DB_CONFIG['DB_PASSWORD']}@{DB_CONFIG['DB_HOST']}:{DB_CONFIG['DB_PORT']}/{DB_CONFIG['DB_NAME']}"
    print(f"Set database URL to: {URL_DATABASE}")

def set_database_engine():
    """Set the database engine, session and base."""
    set_database_url()
    global Engine, SessionLocal, Base
    Engine = create_engine(URL_DATABASE)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=Engine)
    Base = declarative_base()
    print(f"Set database engine to: {Engine}")
    print(f"Set database session to: {SessionLocal}")
    print(f"Set database base to: {Base}")

# if __name__ == "__main__":
set_database_engine()