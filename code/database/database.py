import os

from future.utils import implements_iterator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import dotenv_values
import code.config as config

Engine = None
SessionLocal = None
Base = None

#niet meer nodig
def set_database_url():
    """Set the database URL based on the environment variables."""
    #config.load_env() # load the environment variables from the .env file

    #staat in config nu:
    #global URL_DATABASE
    #URL_DATABASE = f"postgresql://{DB_CONFIG['DB_USER']}:{DB_CONFIG['DB_PASSWORD']}@{DB_CONFIG['DB_HOST']}:{DB_CONFIG['DB_PORT']}/{DB_CONFIG['DB_NAME']}"
    # print(f"Set database URL to: {URL_DATABASE}") # For security, don't print the URL

def set_database_engine():
    """Set the database engine, session and base."""
    config.set_host()
    global Engine, SessionLocal, Base
    secrets = dotenv_values('.env')
    Engine = create_engine(secrets['URL_DATABASE'])
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=Engine)
    Base = declarative_base()
    print(f"Set database engine to: {Engine}")
    # print(f"Set database session to: {SessionLocal}")
    # print(f"Set database base to: {Base}")

set_database_engine()