import os

import sqlalchemy
from fastapi import FastAPI, Depends, HTTPException, Request, BackgroundTasks
import uvicorn

from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import Response

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import PlainTextResponse

from .algoritmes.fuzzy import similarity_score, jaccard_similarity, _most_similar
from .config import API_HOST_URL, API_HOST_PORT, BLOCKED_CONTENT_TAGS, check_key

from src.routes.development.apps import router as apps_router
from .routes.frontend import router as frontend_router, root
from src.routes.development.categories import router_development as categories_router_development
from src.routes.categories import router as categories_router

import src.database.models as models
from tests.integration.fill_database import fill_database

from src.database.database import Engine, get_db, SessionLocal
from prometheus_client import Counter, generate_latest, REGISTRY, start_http_server

http_requests_total = Counter(
    "http_requests_total", "Total HTTP Requests", ["method", "endpoint"]
)


# Middleware to count the requests
class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        # Count the request
        http_requests_total.labels(method=request.method, endpoint=request.url.path).inc()
        return response

class API:
    db_dependency = None

    templates = Jinja2Templates(directory="src/templates")

    def __init__(self):
        """
        The constructor of this API class. executed when app = API() is called. in the main.py file.
        """
        self.app = FastAPI()
        self.app.add_middleware(PrometheusMiddleware)

        self.app.mount("/static", StaticFiles(directory="src/static"), name="static")

        models.Base.metadata.create_all(bind=Engine)

        self.db_dependency = Depends(get_db)

    def run(self):
        """"
        Function to run the API. This function will register all the endpoints and start the API server with uvicorn.

        Using the API_HOST_URL and API_HOST_PORT from the config.py file or the values set in .env
        """
        self.register_endpoints()

        print("Running the API 🚀")

        uvicorn.run(self.app, host=API_HOST_URL, port=API_HOST_PORT, reload=False, log_level="debug", use_colors=True)


    def register_endpoints(self, all_endpoints=False):
        """"
        Function to define all the endpoints for the API.
        """

        self.app.include_router(frontend_router)
        self.app.include_router(categories_router)

        # register routers, only when in PYCHARM or Pytest
        if os.getenv("PYCHARM_HOSTED") or os.getenv("PYTEST_RUNNING") or all_endpoints: # We dont want users on production to modify the database with the CRUD endpoints.
            self.app.include_router(apps_router)
            self.app.include_router(categories_router_development)

        @self.app.get("/")
        async def root():
            return {"message": "Hello, World!"}

        @self.app.get("/metrics")
        async def metrics():
            return Response(generate_latest(REGISTRY), media_type="text/plain")


        @self.app.delete("/stop", include_in_schema=False)
        def stop(background_tasks: BackgroundTasks, key: str):
            if not check_key(key):
                raise HTTPException(status_code=401, detail="Unauthorized")
                return

            background_tasks.add_task(stop_server)
            return {"message": "Stopping server in 5 seconds."}


        def stop_server(seconds: int = 5):
            """" Stop the API server in given seconds. """
            import time
            for i in range(seconds, 0, -1):
                print(f"Stopping server in {i} seconds.")
                time.sleep(1)
            os._exit(1) # Force exit the server

        @self.app.get("/apps")
        def read_apps(db=self.db_dependency, all_fields: bool = False, target_name: str = None, like: str = None):
            """
            Get a JSON / dictionary with all the apps in the database.

            :param all_fields: If True, return all fields of the app, otherwise only the id and name of the app.
            :param target_name: Find the most similar named apps for this name.
            :param like: Find apps with names like this, Uses %string% for SQL LIKE query.
            :return: List of apps in JSON/dictionary format.
            """
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
            """
            Helper function to get the related data for an app. For example, categories, genres or tags. (Not a direct endpoint)
            Based on the model_class and relationship_class provided.

            :param appid: The appid or name of the game to get the related data for.
            :param db: The database dependency.
            :param model_class: The model class to get the related data for. For example, models.Category.
            :param relationship_class: The relationship class which connects the app and the model_class. For example, models.AppCategory.
            :param fuzzy: If True, try to find the app by name even when the grammar is not correct using my fuzzy algorithm ^Seger. It skips this always when the appid is a number.
            :return: List of related data.
            """
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

        @self.app.get("/app/{appid}/categories")
        def read_app_categories(appid: str, fuzzy: bool = True, db=self.db_dependency):
            """"
            Get all the categories for a specific app.

            :param appid: The appid or name of the game to get the categories for.
            :param fuzzy: If True, try to find the app by name even when the grammar is not correct using my fuzzy algorithm ^Seger. It skips this always when the appid is a number.
            :return: List of categories for the app.
            """
            return get_app_related_data(appid, db, models.Category, models.AppCategory, fuzzy)

        @self.app.get("/fill", include_in_schema=False)
        def fill(db=self.db_dependency):
            """
            manually fill the database with testdata if api is hosted by pycharm
            """
            if os.getenv("PYCHARM_HOSTED") or os.getenv("PYTEST_RUNNING"):
                try:
                    fill_database(db)
                except sqlalchemy.exc.IntegrityError:
                    raise HTTPException(status_code=500, detail=f"data is al aanwezig")
            else: raise HTTPException(status_code=401, detail=f"geen pycharm host")

        @self.app.get("/app/{appid}/genres")
        def read_app_genres(appid: str, fuzzy: bool = True, db=self.db_dependency):
            """"
            Get all the genres for a specific app.

            :param appid: The appid or name of the game to get the genres for.
            :param fuzzy: If True, try to find the app by name even when the grammar is not correct using my fuzzy algorithm ^Seger. It skips this always when the appid is a number.
            :return: List of genres for the app.
            """
            return get_app_related_data(appid, db, models.Genre, models.AppGenre, fuzzy)

        @self.app.get("/app/{appid}/tags")
        def read_app_tags(appid: str, fuzzy: bool = True, db=self.db_dependency):
            """
            Get all the tags for a specific app.

            :param appid: The appid or name of the game to get the tags for.
            :param fuzzy: If True, try to find the app by name even when the grammar is not correct using my fuzzy algorithm ^Seger. It skips this always when the appid is a number.
            """
            return get_app_related_data(appid, db, models.Tags, models.AppTags, fuzzy)

        @self.app.get("/app/{appid}")
        def read_app(appid: str, fuzzy: bool = True, db=self.db_dependency):
            """
            Endpoint to get the data for a specific app.

            :param appid: The appid or name of the game to get the data for.
            :param fuzzy: If True, try to find the app by name even when the grammar is not correct using my fuzzy algorithm ^Seger. It skips this always when the appid is a number.
            """
            app = app_data_from_id_or_name(appid, db, fuzzy, False)
            print(app)
            if not app:
                raise HTTPException(status_code=404, detail="App not found.")
            return app

        @self.app.get("/developers")
        def read_developers(db=self.db_dependency, apps = False):
            """
            Get all developers in the database.
            :param apps: If True, also return the apps for developers.
            :return: List of developers in JSON/dictionary format with id and name.
            """
            if apps:
                developers = db.query(models.App.developer, models.App.id, models.App.name).order_by(models.App.id).all()

                if not developers:
                    raise HTTPException(status_code=404, detail="No developers found in the database.")

                developers_result = {}
                for dev in developers:
                    if dev.developer not in developers_result:
                        developers_result[dev.developer] = {"name": dev.developer, "apps": []}
                    developers_result[dev.developer]["apps"].append({
                        "id": dev.id,
                        "name": dev.name
                    })

                if not developers_result:
                    raise HTTPException(status_code=404, detail="No games found for developers in the database.")

                return list(developers_result.values())

            developers = db.query(models.App.developer).distinct().all()
            if not developers:
                raise HTTPException(status_code=404, detail="No developers found in the database.")

            return [{"name": dev.developer} for dev in developers]

        def app_data_from_id_or_name(app_id_or_name: str, db, fuzzy: bool = True, categories: bool = False):
            """"
            Helper function to get the data for a specific app. (Not a direct endpoint)

            :param app_id_or_name: The appid or name of the game to get the data for.
            :param db: The database dependency.
            :param fuzzy: If True, try to find the app by name even when the grammar is not correct using my fuzzy algorithm ^Seger. It skips this always when the appid is a number.
            :param categories: If True, also get the categories, genres and tags for the app in the App object as response.
            :return: JSON / dictionary with all the data for the app.
            """
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

            if categories and app and app.id:
                tags = db.query(models.Tags).join(models.AppTags).filter(models.AppTags.app_id == app.id).all()
                genres = db.query(models.Genre).join(models.AppGenre).filter(models.AppGenre.app_id == app.id).all()
                categories = db.query(models.Category).join(models.AppCategory).filter(
                    models.AppCategory.app_id == app.id).all()

                app.tags = tags
                app.genres = genres
                app.categories = categories

            return app

        @self.app.get("/apps/developer/{target_name}")
        def get_developer_games(target_name: str, fuzzy: bool = True, all_fields: bool = False, db=self.db_dependency):
            """"
            Function to get all games for a specific developer.

            :param target_name: The name of the developer to get the games for.
            :param fuzzy: When True, try to find the most similar named developer in the database. Using my fuzzy algorithm
            :param all_fields: When True, return all fields of the app, otherwise only the id and name of the app will be returned.
            :return: JSON / dictionary with all the games for the given developer.
            """
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
                    raise HTTPException(status_code=404, detail=f"(AttributeError) No apps found for developer {developer}")
                if games:
                    return games
                raise HTTPException(status_code=404, detail=f"No apps found for developer {developer}")
            else:
                raise HTTPException(status_code=404, detail="Developer not found")

        def most_similar_named_developer(target_name: str, db):
            """
            Helper function to find the most similar named developer in the database.

            :param target_name: The name of the developer to find the most similar named developer for.
            :param db: The database dependency.
            :return: String "name" of the most similar named developer.
            """
            developers = db.query(models.App).with_entities(models.App.developer).distinct().all()
            most_similar_dev, similarity = _most_similar(target_name, developers, "developer")

            if most_similar_dev:
                print(f"Most similar developer: {most_similar_dev} with similarity: {similarity}. For target: {target_name}")
                return most_similar_dev.developer

            return None

        @self.app.get("/app/similar/{target_name}")
        def most_similar_named_app(target_name: str, db=self.db_dependency):
            """
            Helper function to find the most similar named app in the database.

            :param target_name: The name of the app to find the most similar named app for.
            :param db: The database dependency.
            :return: Dictionary / JSON with the (id, name and similarity) of the app.
            """

            if target_name.isdigit():
                app = db.query(models.App).filter(models.App.id == int(target_name)).first()
                if app:
                    return {"id": app.id, "name": app.name, "header_image": app.header_image, "similarity": 100}
                return None

            apps = db.query(models.App).with_entities(models.App.id, models.App.name, models.App.header_image).all()
            most_similar_app, similarity = _most_similar(target_name, apps, "name")

            if most_similar_app:
                return {"id": most_similar_app.id, "name": most_similar_app.name, "header_image": most_similar_app.header_image, "similarity": similarity}

            return None

        def find_similar_named_apps(target_name: str, db):
            """
            Helper function to find the most similar named apps in the database.

            :param target_name: The name of the app to find the most similar named apps for.
            :param db: The database dependency.
            :return: Dictionary of multiple apps matching the target_name with their (id, name and similarity.)
            """
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
            """
            Get all apps based on the tag name.

            :param target_name: The name or id of the tag to get the apps for.
            :param fuzzy: If True, try to find the most similar named tag in the database. Using my fuzzy algorithm ^Seger.
            :param all_fields: If True, return all fields of the app, otherwise only the (id, name) of the app will be returned.
            :return: List of apps in JSON/dictionary format.
            """
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

        @self.app.get("/robots.txt", response_class=PlainTextResponse, include_in_schema=False)
        def robots():
            """Don't allow any crawlers to index the API. E.g: Search engines."""
            data = """User-agent: *\nDisallow: /"""
            return data

        print("Registered all endpoints ✨")
