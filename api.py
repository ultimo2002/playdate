from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
import uvicorn

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from config import API_HOST_URL, API_HOST_PORT, load_env, DB_CONFIG
from steam_api import get_app_details

class API:
    def __init__(self):
        self.app = FastAPI()

    def run(self):
        self.register_endpoints()

        uvicorn.run(self.app, host=API_HOST_URL, port=API_HOST_PORT, reload=False)

    def register_endpoints(self):

        # get all from database
        @self.app.get("/all_test")
        def all_test():
            items = self.app.state.db.fetch("SELECT datname FROM pg_database WHERE datistemplate = false;")
            return items

        @self.app.get("/")
        async def root(db: Session = Depends(get_db)):
            return {"message": "Hello World"}

        # a test getting app details from the Steam API
        # TODO: Remove this endpoint, when database is implemented
        @self.app.get("/app/{app_id}")
        def read_app(app_id: int):
            app_details = get_app_details(app_id)
            if app_details:
                if not isinstance(app_details, dict):
                    app_details = app_details.to_dict()

                return app_details
            else:
                return {"message": "App not found"}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

if __name__ == "__main__":
    load_env()

    database_url = f"postgresql://{DB_CONFIG['DB_USER']}:{DB_CONFIG['DB_PASSWORD']}@{DB_CONFIG['DB_HOST']}:{DB_CONFIG['DB_PORT']}/{DB_CONFIG['DB_NAME']}"
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    api = API()
    api.run()