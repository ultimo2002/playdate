
import os
import time

from fastapi import FastAPI, Depends
import uvicorn

from config import API_HOST_URL, API_HOST_PORT, ADDED_GAMES_LIST_CACHE_FILE
from steam_api import get_app_details, fetch_app_list, get_current_player_count

import models
from database import Engine, SessionLocal


class API:
    db_dependency = None

    def __init__(self):
        self.app = FastAPI()

        # set_database_engine() # Make sure the database engine is set
        models.Base.metadata.create_all(bind=Engine)

        self.db_dependency = Depends(self.get_db)


    def run(self):
        self.register_endpoints()

        print("Run API")

        uvicorn.run(self.app, host=API_HOST_URL, port=API_HOST_PORT, reload=False)

    def get_db(self):
        """Get db dependency, don't touch!"""
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

        # function to fill the category table with all categories from the Steam API
        def fill_category_table(db = self.db_dependency, categories = None):
            try:
                for category in categories:
                    db.add(models.Category(id=category["id"], name=category["description"]))
            except Exception as e:
                print(f"Error: {e}")
            db.commit()
            db.refresh(models.Category)

        # Endpoint to fill the app table with all apps from the Steam API
        # @self.app.get("/fill_app_table")
        def fill_app_table(db = self.db_dependency):
            app_list = fetch_app_list()

            added_apps = 0

            # create dirs if they don't exist
            os.makedirs(os.path.dirname(ADDED_GAMES_LIST_CACHE_FILE), exist_ok=True)

            added_games = []

            try:
                # skip to the front the last app id from the file, only do the appids that are not in the file
                # by removing the appids that are already in the file
                with open(ADDED_GAMES_LIST_CACHE_FILE, 'r') as file:
                    added_games = file.readlines()
            except FileNotFoundError:
                pass

            for app in app_list:
                try:
                    appid = int(app["appid"])
                    # skip the app if it's already in the file
                    if f"{appid}\n" in added_games:
                        continue

                    name = str(app["name"])
                    if not name:
                        continue
                except (KeyError, ValueError):
                    continue

                # add app id to a file to continue from there later on
                with open(ADDED_GAMES_LIST_CACHE_FILE, 'a') as file:
                    file.write(f"{appid}\n")

                player_count = get_current_player_count(appid)
                if player_count < 500:
                    continue

                details = get_app_details(appid)
                if details:
                    # platform as comma separated string, need to be different maybe
                    platform = ''
                    if details["platforms"] and details["platforms"].keys():
                        platform = ", ".join(details["platforms"].keys())

                    developer = details["developers"][0] if details["developers"] else ''

                    db.add(models.App(app_id=appid, name=name, player_count=player_count, platform=platform, developer=developer))

                    try:
                        # try get categories to use in the fill_category_table function
                        categories = details["categories"]
                        fill_category_table(db, categories)
                    except KeyError:
                        print(f"No categories found for appid: {appid}, name: {name}")

                added_apps += 1

                db.commit()

                db.refresh(models.App)
                db.refresh(models.Category)

                time.sleep(0.5) # Sleep for 0.5 seconds to not overload the API

            return {"added_apps": added_apps}


if __name__ == "__main__":
    api = API()
    api.run()