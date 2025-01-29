from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
import uvicorn

from sqlalchemy.orm import Session
from sqlalchemy.sql.annotation import Annotated

from config import API_HOST_URL, API_HOST_PORT, load_env, DB_CONFIG
from steam_api import get_app_details, fetch_app_list

import models
from database import Engine, SessionLocal, set_database_engine


class API:
    db_dependency = None

    def __init__(self):
        self.app = FastAPI()

        # set_database_engine() # Make sure the database engine is set
        models.Base.metadata.create_all(bind=Engine)

        self.db_dependency = Depends(self.get_db)


    def run(self):
        self.register_endpoints()

        uvicorn.run(self.app, host=API_HOST_URL, port=API_HOST_PORT, reload=False)

        print("Run API")

    def get_db(self):
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()


    def register_endpoints(self):
        @self.app.get("/")
        def root():
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

        # test endpoint to create a new app in the database with a name and appid
        @self.app.get("/test_create_app")
        def create_app(db = self.db_dependency):
            app = models.App(name="Seger", id=1)
            db.add(app)
            db.commit()
            db.refresh(app)
            return app

        # Endpoint to fill the app table with all apps from the Steam API
        @self.app.get("/fill_app_table")
        def fill_app_table(db = self.db_dependency):
            app_list = fetch_app_list()
            for app in app_list:
                appid = app["appid"]
                name = app["name"]

                if not name:
                    continue

                # details = get_app_details(appid)

            return {"message": "App table filled"}

            

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

if __name__ == "__main__":
    api = API()
    api.run()