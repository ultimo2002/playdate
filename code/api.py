import os
import asyncio

from fastapi import FastAPI, Depends, Request, BackgroundTasks, HTTPException
import uvicorn

from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from sqlalchemy.sql import text

from algoritms import similarity_score, jaccard_similarity, _most_similar
from config import API_HOST_URL, API_HOST_PORT, ADDED_GAMES_LIST_CACHE_FILE, TextStyles
from steam_api import get_app_details, fetch_app_list, get_current_player_count, get_steam_tags

import models
from database import Engine, SessionLocal


class API:
    db_dependency = None

    templates = Jinja2Templates(directory="templates")

    def __init__(self):
        self.app = FastAPI()

        self.app.mount("/static", StaticFiles(directory="static"), name="static")

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

        @self.app.get("/apps")
        def read_apps(db=self.db_dependency, all_fields: bool = False, target_name: str = None, like: str = None):
            if target_name:
                return find_similar_named_apps(target_name, db)
            elif like:
                like = like.strip().lower()
                apps = db.query(models.App).filter(models.App.name.ilike(f"%{like}%")).all()
                if not apps:
                    raise HTTPException(status_code=404, detail=f"No apps found with name like '{like}'")
                return apps
            if all_fields:
                apps = db.query(models.App).all()
                return apps

            apps = db.query(models.App.id, models.App.name).all()
            return [{"id": app.id, "name": app.name} for app in apps]

        def get_app_related_data(appid: str, db, model_class, relationship_class):
            """Get the related data for the app, like categories, genres or tags."""
            if appid.isdigit():
                appid = int(appid)
            else:
                app = app_data_from_id_or_name(str(appid), db)
                appid = int(app.id)

            related_data = db.query(model_class).join(relationship_class).filter(
                relationship_class.app_id == appid).all()

            if not related_data:
                raise HTTPException(status_code=404, detail=f"App and/or {model_class.__name__.lower()} not found")

            return related_data

        @self.app.get("/app/{appid}/categories")
        def read_app_categories(appid: str, db=self.db_dependency):
            return get_app_related_data(appid, db, models.Category, models.AppCategory)

        @self.app.get("/app/{appid}/genres")
        def read_app_genres(appid: str, db=self.db_dependency):
            return get_app_related_data(appid, db, models.Genre, models.AppGenre)

        @self.app.get("/app/{appid}/tags")
        def read_app_tags(appid: str, db=self.db_dependency):
            return get_app_related_data(appid, db, models.Tags, models.AppTags)

        @self.app.get("/app/{appid}")
        def read_app(appid: str, db=self.db_dependency):
            return app_data_from_id_or_name(appid, db)

        @self.app.put("/app/{appid}")
        def update_app(appid: int, name: str, db=self.db_dependency):
            app = db.query(models.App).filter(models.App.id == appid).first()
            if app:
                app.name = name
                db.commit()
                db.refresh(app)
                return app
            else:
                raise HTTPException(status_code=404, detail="App not found")

        @self.app.post("/app")
        def add_app(name: str, appid: int, short_description: str = "", price: str = "", developer: str = "Seger", header_image: str = "", background_image: str = "", db=self.db_dependency):
            if not os.environ.get("PYCHARM_HOSTED"):
                raise HTTPException(status_code=403, detail="This endpoint is only available in the development environment.")

            name = name.replace("%20", " ")
            name.strip()

            app = models.App(name=name, id=appid, short_description=short_description, price=price, developer=developer, header_image=header_image, background_image=background_image)
            db.add(app)
            db.commit()
            db.refresh(app)
            return app

        @self.app.delete("/app/{appid}")
        def delete_app(appid: int, db=self.db_dependency):
            if not os.environ.get("PYCHARM_HOSTED"):
                raise HTTPException(status_code=403, detail="This endpoint is only available in the development environment.")

            app = db.query(models.App).filter(models.App.id == appid).first()

            if app:
                # delete also the app-category and app-genre app-tag relations
                db.query(models.AppCategory).filter(models.AppCategory.app_id == appid).delete()
                db.query(models.AppGenre).filter(models.AppGenre.app_id == appid).delete()
                db.query(models.AppTags).filter(models.AppTags.app_id == appid).delete()

                db.delete(app)

                db.commit()
                return {"message": f"App {appid} deleted"}
            else:
                raise HTTPException(status_code=404, detail=f"App {appid} not found")

        def app_data_from_id_or_name(app_id_or_name: str, db=self.db_dependency):
            app = None

            if app_id_or_name.isdigit():
                app = db.query(models.App).filter(models.App.id == int(app_id_or_name)).first()
            else:
                similar_app = most_similar_named_app(app_id_or_name, db)
                if similar_app and isinstance(similar_app.get("id"), int):
                    app = db.query(models.App).filter(models.App.id == similar_app["id"]).first()

            return app

        @self.app.get("/apps/developer/{target_name}")
        def get_developer_games(target_name: str, db=self.db_dependency):
            target_name = target_name.strip().lower()

            similar_developer = most_similar_named_developer(target_name, db)

            if similar_developer:
                developer = str(similar_developer)
                games = db.query(models.App).filter(models.App.developer == developer).all()
                if games:
                    return games
                raise HTTPException(status_code=404, detail=f"No games found for developer {developer}")
            else:
                raise HTTPException(status_code=404, detail="Developer not found")

        def most_similar_named_developer(target_name: str, db=self.db_dependency):
            """Find the most similar named developer in the database."""
            developers = db.query(models.App).with_entities(models.App.developer).distinct().all()
            most_similar_dev, similarity = _most_similar(target_name, developers, "developer")

            if most_similar_dev:
                print(f"Most similar developer: {most_similar_dev} with similarity: {similarity}. For target: {target_name}")
                return most_similar_dev.developer

            return None

        def most_similar_named_app(target_name: str, db=self.db_dependency):
            """Find the most similar named app in the database."""
            apps = db.query(models.App).with_entities(models.App.id, models.App.name).all()
            most_similar_app, similarity = _most_similar(target_name, apps, "name")

            if most_similar_app:
                return {"id": most_similar_app.id, "name": most_similar_app.name, "similarity": similarity}

            return None

        def find_similar_named_apps(target_name: str, db=self.db_dependency):
            target_name = target_name.strip().lower()

            apps = db.query(models.App).with_entities(models.App.id, models.App.name).all()

            similar_apps = []

            TRESHOLD = 60
            JACCARD_TRESHOLD = 25

            for app in apps:
                levenshtein_sim = similarity_score(target_name, app.name)
                jaccard_sim = jaccard_similarity(target_name, app.name)

                if levenshtein_sim >= TRESHOLD or jaccard_sim >= JACCARD_TRESHOLD:
                    similar_apps.append({"id": app.id, "name": app.name, "similarity": round(max(levenshtein_sim, jaccard_sim), 2)})

            return sorted(similar_apps, key=lambda x: x["similarity"], reverse=True)

        # function to fill the category table with all categories from the Steam API
        def fill_category_table(db = self.db_dependency, categories = None, appid = None, genre = False):
            if categories:
                new_categories = []

                if not genre:
                    existing_category_ids = {category.id for category in db.query(models.Category.id).all()}

                    new_categories = [
                        models.Category(id=category["id"], name=category["description"])
                        for category in categories if int(category["id"]) not in existing_category_ids
                    ]
                else:
                    existing_genre_ids = {genre.id for genre in db.query(models.Genre.id).all()}

                    new_categories = [
                        models.Genre(id=category["id"], name=category["description"])
                        for category in categories if int(category["id"]) not in existing_genre_ids
                    ]

                if new_categories:
                    # check for duplicate categorie names in the database
                    existing_category_names = {category.name for category in db.query(models.Category.name).all()}
                    # When it does exist add a number at the end of the name
                    for category in new_categories:
                        if category.name in existing_category_names:
                            i = 1
                            while f"{category.name} ({i})" in existing_category_names:
                                i += 1
                            category.name = f"{category.name} ({i})"
                            existing_category_names.add(category.name)
                        else:
                            existing_category_names.add(category.name)

                    db.add_all(new_categories)
                    db.commit()
                    print(f"Inserted {len(new_categories)} new {'genres' if genre else 'categories'}.")

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

        @self.app.get("/fill_tags_table")
        async def fill_tags_table(background_tasks: BackgroundTasks, db=self.db_dependency):
            if not os.environ.get("PYCHARM_HOSTED"):
                raise HTTPException(status_code=403, detail="This endpoint is only available in the development environment.")

            # Call the function to run in the background
            background_tasks.add_task(run_fill_tags_table, db)
            return {"message": "The tags table filling task has started in the background."}

        @self.app.get("/delete_tags")
        async def delete_tags(db=self.db_dependency):
            if not os.environ.get("PYCHARM_HOSTED"):
                raise HTTPException(status_code=403, detail="This endpoint is only available in the development environment.")

            db.execute(text(f"TRUNCATE TABLE {models.Tags.__tablename__}, {models.AppTags.__tablename__} RESTART IDENTITY CASCADE"))
            db.commit()
            print("Deleted all tags and app-tag relations from the database. A clean start...")
            return {"message": "Deleted all tags and app-tag relations from the database. A clean start..."}

        async def run_fill_tags_table(db):
            # get the apps that do not have tags related to them yet
            apps = db.query(models.App).filter(~models.App.id.in_(db.query(models.AppTags.app_id))).all()

            current_index = 0
            len_apps = len(apps)

            for app in apps:
                current_index += 1
                print(f"Processing app {app.id} ({current_index}/{len_apps})")
                await asyncio.sleep(0.25)
                tags = get_steam_tags(app.id)
                if tags:
                    # check if tags already exist in the database
                    existing_tags = {tag.name for tag in db.query(models.Tags.name).all()}
                    new_tags = [
                        models.Tags(name=tag)
                        for tag in tags if tag not in existing_tags
                    ]

                    if new_tags:
                        db.add_all(new_tags)
                        db.commit()

                    print(f"Inserted {len(new_tags)} new tags from app {app.id} .")

                    # Insert the app-tag relations
                    app_tags = [
                        models.AppTags(app_id=app.id, tag_id=tag.id)
                        for tag in db.query(models.Tags).filter(models.Tags.name.in_(tags)).all()
                    ]
                    if app_tags:
                        db.add_all(app_tags)
                        db.commit()

                    print(f"Inserted {len(app_tags)} app-tag relations for app {app.id} .")
                else:
                    print(f"No tags found for app {app.id} .")

        # Endpoint to fill the app table with all apps from the Steam API
        @self.app.get("/fill_app_table")
        async def fill_app_table(background_tasks: BackgroundTasks, db=self.db_dependency):
            if not os.environ.get("PYCHARM_HOSTED"):
                raise HTTPException(status_code=403, detail="This endpoint is only available in the development environment.")

            # Call the function to run in the background
            background_tasks.add_task(run_fill_app_table, db)
            return {"message": "The app table filling task has started in the background."}

        @self.app.get("/fetch_app/{appid}")
        async def fetch_app(appid: int, db=self.db_dependency):
            """"
            Fetch the app details from the Steam API and add it to the database.
            Doesn't look at the player count, just fetches the details and adds it to the database.
            Used for adding every app you want to the database.
            """
            if not os.environ.get("PYCHARM_HOSTED"):
                raise HTTPException(status_code=403, detail="This endpoint is only available in the development environment.")

            app = db.query(models.App).filter(models.App.id == appid).first()
            if app:
                raise HTTPException(status_code=409, detail=f"App {appid} already exists in the database.")

            details = get_app_details(appid)
            if details:
                os.makedirs(os.path.dirname(ADDED_GAMES_LIST_CACHE_FILE), exist_ok=True)
                with open(ADDED_GAMES_LIST_CACHE_FILE, 'a') as file:
                    file.write(f"{appid}\n")

                name = details["name"]
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

                print(f"Processing appid {appid}: {name}")

                app = models.App(id=appid, name=name, developer=developer, header_image=header_image, price=price, background_image=background_image, short_description=short_description)
                db.add(app)
                db.commit()
                db.refresh(app)

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

                return app
            else:
                raise HTTPException(status_code=404, detail=f"App details {appid} not found in the Steam API.")

        async def run_fill_app_table(db):
            # return # Remove this line when the function is implemented

            apps_looped = 0

            app_list = fetch_app_list()
            added_apps = 0

            os.makedirs(os.path.dirname(ADDED_GAMES_LIST_CACHE_FILE), exist_ok=True)

            database_games = db.query(models.App.id).all()
            print(f"Total games in the database: {len(database_games)}")

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

                try:
                    appid = int(app["appid"])
                    # Skip if the app is already in the file
                    if f"{appid}\n" in added_games:
                        continue

                    if appid in [game.id for game in database_games]:
                        continue

                    name = str(app["name"])
                    if not name:
                        continue

                    if 'DLC' in name.lower() or 'trailer' in name.lower():
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

                    app = models.App(id=appid, name=name, developer=developer, header_image=header_image, price=price, background_image=background_image, short_description=short_description)
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

                await asyncio.sleep(0.25)

            print(f"Total apps added: {added_apps}")

if __name__ == "__main__":
    api = API()
    api.run()
