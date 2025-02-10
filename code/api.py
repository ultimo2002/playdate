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

        def get_app_related_data(appid: str, db, model_class, relationship_class, fuzzy: bool = True):
            """Get the related data for the app, like categories, genres or tags."""
            if appid.isdigit():
                appid = int(appid)
            else:
                if fuzzy:
                    app = app_data_from_id_or_name(str(appid), db)
                    appid = int(app.id)
                else:
                    appid = appid.strip().capitalize()
                    app = db.query(models.App).filter(models.App.name == appid).first()
                    if not app:
                        raise HTTPException(status_code=404, detail=f"App {appid} not found")
                    appid = int(app.id)

            related_data = db.query(model_class).join(relationship_class).filter(
                relationship_class.app_id == appid).all()

            if not related_data:
                raise HTTPException(status_code=404, detail=f"App and/or {model_class.__name__.lower()} not found")

            return related_data

        @self.app.get("/cats")
        def read_cats(db=self.db_dependency):
            """Get all categories, genres and tags in one request."""
            return {
                "tags": db.query(models.Tags).all(),
                "categories": db.query(models.Category).all(),
                "genres": db.query(models.Genre).all(),
            }

        @self.app.get("/tags")
        def read_tags(db=self.db_dependency):
            tags = db.query(models.Tags).all()
            return tags

        @self.app.get("/categories")
        def read_categories(db=self.db_dependency):
            categories = db.query(models.Category).all()
            return categories

        @self.app.get("/genres")
        def read_genres(db=self.db_dependency):
            genres = db.query(models.Genre).all()
            return genres

        @self.app.get("/app/{appid}/categories")
        def read_app_categories(appid: str, fuzzy: bool = True, db=self.db_dependency):
            return get_app_related_data(appid, db, models.Category, models.AppCategory, fuzzy)

        @self.app.get("/app/{appid}/genres")
        def read_app_genres(appid: str, fuzzy: bool = True, db=self.db_dependency):
            return get_app_related_data(appid, db, models.Genre, models.AppGenre, fuzzy)

        @self.app.get("/app/{appid}/tags")
        def read_app_tags(appid: str, fuzzy: bool = True, db=self.db_dependency):
            return get_app_related_data(appid, db, models.Tags, models.AppTags, fuzzy)

        @self.app.get("/app/{appid}")
        def read_app(appid: str, fuzzy: bool = True, db=self.db_dependency):
            return app_data_from_id_or_name(appid, db, fuzzy)

        @self.app.put("/app/{appid}/tag/{tagid}")
        def add_app_tag(appid: int, tagid: int, db=self.db_dependency):
            if not os.environ.get("PYCHARM_HOSTED"):
                raise HTTPException(status_code=403, detail="This endpoint is only available in the development environment.")
            elif not tagid or not appid:
                raise HTTPException(status_code=400, detail="Tag and app id required.")

            app = db.query(models.App).filter(models.App.id == appid).first()
            tag = db.query(models.Tags).filter(models.Tags.id == tagid).first()

            # check if the app not already has this tag
            app_tag = db.query(models.AppTags).filter(models.AppTags.app_id == appid, models.AppTags.tag_id == tagid).first()
            if app_tag:
                raise HTTPException(status_code=409, detail="App already has this tag.")

            if app and tag:
                print(f"Adding tag {tagid} to app {appid}")
                app_tag = models.AppTags(app_id=appid, tag_id=tagid)
                db.add(app_tag)
                db.commit()
                db.refresh(app_tag)
                return app_tag
            else:
                raise HTTPException(status_code=404, detail="App or category not found")

        @self.app.delete("/app/{appid}/tag/{tagid}")
        def delete_app_tag(appid: int, tagid: int, db=self.db_dependency):
            if not os.environ.get("PYCHARM_HOSTED"):
                raise HTTPException(status_code=403, detail="This endpoint is only available in the development environment.")
            elif not tagid or not appid:
                raise HTTPException(status_code=400, detail="Tag and app id required.")

            app_tag = db.query(models.AppTags).filter(models.AppTags.app_id == appid, models.AppTags.tag_id == tagid).first()
            if app_tag:
                db.delete(app_tag)
                db.commit()
                return {"message": f"Tag {tagid} deleted from app {appid}"}
            else:
                raise HTTPException(status_code=404, detail="App-tag relation not found")

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

        def app_data_from_id_or_name(app_id_or_name: str, db=self.db_dependency, fuzzy: bool = True):
            app = None

            if app_id_or_name.isdigit():
                app = db.query(models.App).filter(models.App.id == int(app_id_or_name)).first()
            else:
                if fuzzy:
                    similar_app = most_similar_named_app(app_id_or_name, db)
                    if similar_app and isinstance(similar_app.get("id"), int):
                        print(f"Most similar app for '{app_id_or_name}' is '{similar_app['name']}' with similarity: {similar_app['similarity']}")
                        app = db.query(models.App).filter(models.App.id == similar_app["id"]).first()
                else:
                    app_id_or_name = app_id_or_name.strip().capitalize()
                    app = db.query(models.App).filter(models.App.name == app_id_or_name).first()
                    if not app:
                        raise HTTPException(status_code=404, detail=f"App {app_id_or_name} not found")

            return app

        @self.app.get("/apps/developer/{target_name}")
        def get_developer_games(target_name: str, fuzzy: bool = True, all_fields: bool = False, db=self.db_dependency):
            target_name = target_name.strip().capitalize()

            similar_developer = target_name
            if fuzzy:
                similar_developer = most_similar_named_developer(target_name, db)

            if similar_developer:
                developer = str(similar_developer)
                try:
                    if all_fields:
                        games = db.query(models.App).filter(models.App.developer == developer).all()
                    else:
                        games = db.query(models.App.id, models.App.name).filter(models.App.developer == developer).all()
                        games = [{"id": game.id, "name": game.name} for game in games]
                except AttributeError:
                    raise HTTPException(status_code=404, detail=f"(AttributeError) No games found for developer {developer}")
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

        @self.app.get("/apps/tag/{target_name}")
        def get_apps_based_on_tag_name(target_name: str, fuzzy: bool = True, all_fields: bool = False, db=self.db_dependency):
            target_name = target_name.strip()
            tag = target_name.capitalize() if not target_name.isupper() else target_name

            def _fetch_apps(filter_condition):
                if all_fields:
                    apps = db.query(models.App).join(models.AppTags).join(models.Tags).filter(filter_condition).all()
                else:
                    apps = db.query(models.App.id, models.App.name).join(models.AppTags).join(models.Tags).filter(
                        filter_condition).all()
                    apps = [{"id": app.id, "name": app.name} for app in apps]

                if not apps:
                    raise HTTPException(status_code=404, detail=f"No apps found for tag {tag}")
                return apps

            if tag.isdigit():
                try:
                    return _fetch_apps(models.Tags.id == int(tag))
                except AttributeError:
                    raise HTTPException(status_code=404, detail=f"(AttributeError) No apps found with tag id {tag}")

            if fuzzy:
                print(f"Searching for similar tag name for '{target_name}'")
                tags = db.query(models.Tags.name).all()
                most_similar_tag, _ = _most_similar(target_name, tags, "name")
                print(f"Most similar tag for '{target_name}' is '{most_similar_tag.name}'")
                tag = most_similar_tag.name if most_similar_tag else target_name

            try:
                return _fetch_apps(models.Tags.name == tag)
            except AttributeError:
                raise HTTPException(status_code=404, detail=f"(AttributeError) No apps found with tag name '{tag}'")

if __name__ == "__main__":
    api = API()
    api.run()
