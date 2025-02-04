import os
import time

from fastapi import FastAPI, Depends, Request, BackgroundTasks
import uvicorn

from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from config import API_HOST_URL, API_HOST_PORT, ADDED_GAMES_LIST_CACHE_FILE, TextStyles
from steam_api import get_app_details, fetch_app_list, get_current_player_count

import models
from database import Engine, SessionLocal


class API:
    db_dependency = None

    templates = Jinja2Templates(directory="templates")

    def __init__(self):
        self.app = FastAPI()

        self.app.mount("/static", StaticFiles(directory="static"), name="static")

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
        @self.app.get("/", response_class=HTMLResponse)
        def root(request: Request):
            # return {"message": "Hello World, auto deploy is working!"}
            return self.templates.TemplateResponse(
                request=request, name="index.html", context={"message": "Hello world!"}
            )

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

        #TODO: IMPORTANT: Remove this endpoint after testing and creating database models. We dont want this endpoint in the final version, everyone can delete all data.
        @self.app.get("/delete_all_data")
        def delete_all_data(db = self.db_dependency):
            if not os.environ.get("PYCHARM_HOSTED"):
                return {"message": "This endpoint is only available in the development environment."}

            try:
                db.query(models.App).delete()
                db.query(models.Category).delete()
                db.query(models.AppCategory).delete()
                db.commit()
                return {"message": "All data deleted."}
            except Exception as e:
                return {"message": f"Error deleting all data: {e}"}

        # function to fill the category table with all categories from the Steam API
        def fill_category_table(db = self.db_dependency, categories = None, appid = None, genre = False):
            if categories:
                # Get all existing category IDs from the database

                if not genre:
                    existing_category_ids = {category.id for category in db.query(models.Category.id).all()}

                    for category in categories:
                        if int(category["id"]) not in existing_category_ids:
                            cat = models.Category(id=category["id"], name=category["description"])
                            try:
                                db.add(cat)
                                db.commit()
                            except Exception as e:
                                print(f"Error while filling the {'genres' if genre else 'categories'} table: {e}")
                else:
                    existing_genre_ids = {genre.id for genre in db.query(models.Genre.id).all()}
                    print(f"Existing genre ids: {existing_genre_ids}")

                    for genre in categories:
                        if int(genre['id']) not in existing_genre_ids:
                            gen = models.Genre(id=genre['id'], name=genre['description'])
                            try:
                                db.add(gen)
                                db.commit()
                            except Exception as e:
                                print(f"Error while filling the {'genres' if genre else 'categories'} table: {e}")

                if not appid:
                    return

                # Insert the app-category relations
                if not genre:
                    app_categories = [
                        models.AppCategory(app_id=appid, category_id=category["id"])
                        for category in categories
                    ]
                else:
                    app_categories = [
                        models.AppGenre(app_id=appid, genre_id=category["id"])
                        for category in categories
                    ]
                db.add_all(app_categories)
                db.commit()
                print(f"Inserted {len(app_categories)} app-{'genre' if genre else 'category'} relations.")


        # Endpoint to fill the app table with all apps from the Steam API
        @self.app.get("/fill_app_table")
        def fill_app_table(background_tasks: BackgroundTasks, db=self.db_dependency):
            if not os.environ.get("PYCHARM_HOSTED"):
                return {"message": "This endpoint is only available in the development environment."}

            # Call the function to run in the background
            background_tasks.add_task(run_fill_app_table, db)
            return {"message": "The app table filling task has started in the background."}

        def run_fill_app_table(db):
            # return # Remove this line when the function is implemented

            apps_looped = 0

            app_list = fetch_app_list()
            added_apps = 0

            os.makedirs(os.path.dirname(ADDED_GAMES_LIST_CACHE_FILE), exist_ok=True)

            # Read the already added games from file
            added_games = set()
            try:
                with open(ADDED_GAMES_LIST_CACHE_FILE, 'r') as file:
                    added_games = set(file.readlines())
            except FileNotFoundError:
                pass

            total_apps = len(app_list)
            for line in added_games:
                apps_looped += 1

            for app in app_list:
                apps_looped += 1
                # APPS_LOOPED_COUNT = 1000
                # if apps_looped > APPS_LOOPED_COUNT: # limit for testing
                #     break

                try:
                    appid = int(app["appid"])
                    # Skip if the app is already in the file
                    if f"{appid}\n" in added_games:
                        continue

                    name = str(app["name"])
                    if not name:
                        continue

                except (KeyError, ValueError):
                    continue

                # Add app id to the file to continue from there later
                with open(ADDED_GAMES_LIST_CACHE_FILE, 'a') as file:
                    file.write(f"{appid}\n")

                MIN_PLAYER_COUNT = 500

                player_count = get_current_player_count(appid)

                if player_count < MIN_PLAYER_COUNT:
                    print(f"{TextStyles.grey}Skipping appid {appid}: {name} (player count: {player_count}) (app {apps_looped}/{total_apps}){TextStyles.reset}")
                    continue

                print(f"Processing appid {appid}: {name} (player count: {player_count}) (app {apps_looped}/{total_apps})")
                details = get_app_details(appid)
                if details:
                    # Platform as a comma-separated string
                    platform = ", ".join(details["platforms"].keys()) if details["platforms"] else ""
                    developer = details["developers"][0] if details["developers"] else ''
                    header_image = details["header_image"] if details["header_image"] else ''
                    background_image = details["background"] if details["background"] else ''
                    short_description = details["short_description"] if details["short_description"] else ''
                    price = ""
                    try:
                        if details['price_overview'] and details['price_overview']['final_formatted']:
                            price = details['price_overview']['final_formatted']
                    except KeyError:
                        pass

                    app = models.App(id=appid, name=name, platform=platform, developer=developer, header_image=header_image, price=price, background_image=background_image, short_description=short_description)
                    db.add(app)
                    db.commit()
                    db.refresh(app)

                    # Attempt to get categories
                    categories = details.get("categories", [])
                    if categories:
                        fill_category_table(db, categories, appid, genre=False)
                    else:
                        print(f"No categories found for appid: {appid}, name: {name}")

                    genres = details.get("genres", [])
                    if genres:
                        fill_category_table(db, genres, appid, genre=True)
                    else:
                        print(f"No genres found for appid: {appid}, name: {name}")

                added_apps += 1

                time.sleep(0.25)

            print(f"Total apps added: {added_apps}")

if __name__ == "__main__":
    api = API()
    api.run()
