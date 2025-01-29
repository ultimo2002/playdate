import time

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from config import DB_CONFIG, load_env, TextStyles

URL_DATABASE = 'postgresql://user:password@localhost:5432/database'

Engine = None
SessionLocal = None
Base = None


def is_database_online(tries: int = 7, wait_time: int = 2) -> bool:
    """ Check if the database is online within the given number of tries.
    Returns: bool: True if the database is online, False otherwise.
    """
    start_time = time.time()

    timeout = wait_time * tries

    while (time.time() - start_time) < timeout:
        try:
            with Engine.connect() as conn:
                conn.execute("SELECT id FROM apps")  # Simple query to check the connection
                print("Database is online.")
                return True
        except Exception:
            print(f"Database not reachable, {TextStyles.grey}({time.time() - start_time:.2f}s) {TextStyles.yellow}retrying in 2 seconds...{TextStyles.reset} max tries: {timeout // wait_time}, Current try: {int((time.time() - start_time) // wait_time) + 1}")
            time.sleep(wait_time)  # Wait before retrying

    print("Database did not respond within the timeout period.")
    print(f"{TextStyles.magenta}{TextStyles.bold}Database is offline or the connection parameters (.env file) are incorrect.{TextStyles.reset}")
    return False

def set_database_url():
    """Set the database URL based on the environment variables."""
    load_env() # load the environment variables from the .env file

    global URL_DATABASE
    URL_DATABASE = f"postgresql://{DB_CONFIG['DB_USER']}:{DB_CONFIG['DB_PASSWORD']}@{DB_CONFIG['DB_HOST']}:{DB_CONFIG['DB_PORT']}/{DB_CONFIG['DB_NAME']}"
    # print(f"Set database URL to: {URL_DATABASE}")

def set_database_engine():
    """Set the database engine, session and base."""
    set_database_url()

    if not is_database_online():
        raise Exception("Database is not online, please check the connection parameters.")

    global Engine, SessionLocal, Base
    Engine = create_engine(URL_DATABASE)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=Engine)
    Base = declarative_base()
    print(f"Set database engine to: {Engine}")
    print(f"Set database session to: {SessionLocal}")
    print(f"Set database base to: {Base}")

# if __name__ == "__main__":
set_database_engine()