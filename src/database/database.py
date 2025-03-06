from exceptiongroup import catch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv  # Import the load_dotenv function

# Load environment variables from .env file
load_dotenv()

URL_DATABASE = os.getenv("URL_DATABASE")


"""Set the database engine, session and base."""

try:
    if "sqlite" in URL_DATABASE:
        Engine = create_engine(URL_DATABASE, connect_args={"check_same_thread": False}).connect()
    else:
        Engine = create_engine(URL_DATABASE)
except Exception as e:
    print(f"Error bij maken van engine, \n URL: {URL_DATABASE}")
    exit(1)
#Engine = create_engine(URL_DATABASE)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=Engine)
Base = declarative_base()
print(f"Set database engine to: {Engine}")
# print(f"Set database session to: {SessionLocal}")
# print(f"Set database base to: {Base}")



def get_db():

    """Get db dependency, don't touch!
    This makes a new database session for the request and closes it after the request is done.
    """


    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
