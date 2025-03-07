import os

from fastapi import FastAPI, Depends, HTTPException, Request
import uvicorn

from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from sqlalchemy.sql.expression import func
from starlette.responses import PlainTextResponse

from src.algoritmes.cache import cache_background_image, cache_header_image
from .algoritmes.fuzzy import similarity_score, jaccard_similarity, _most_similar, make_typo
from .config import API_HOST_URL, API_HOST_PORT, BLOCKED_CONTENT_TAGS

from src.routes.development.apps import router as apps_router
from .routes.frontend import router as frontend_router, root
from src.routes.development.categories import router_development as categories_router_development
from src.routes.categories import router as categories_router

import src.database.models as models
from tests.fill_database import fill_database

from src.database.database import Engine, get_db, SessionLocal


class API:
    db_dependency = None

    templates = Jinja2Templates(directory="src/templates")

    def __init__(self):
        """
        The constructor of this API class. executed when app = API() is called. in the main.py file.
        """
        self.app = FastAPI()

        self.app.mount("/static", StaticFiles(directory="src/static"), name="static")

        models.Base.metadata.create_all(bind=Engine)

        self.db_dependency = Depends(get_db)

    def run(self):
        """"
        Function to run the API. This function will register all the endpoints and start the API server with uvicorn.

        Using the API_HOST_URL and API_HOST_PORT from the config.py file or the values set in .env
        """
        self.register_endpoints()

        print("Run API")

        uvicorn.run(self.app, host=API_HOST_URL, port=API_HOST_PORT, reload=False, log_level="debug", use_colors=True)

    def get_random_apps(db = db_dependency, count: int = 15):
        """
        Get a dictionary with random apps from the database. With typo's in the names.
        :param count: The amount of random apps to return.
        :return: Dictionary with given count random apps with their id and name.
        """
        # maximal 25 apps, minimal 1 app, clamp the count
        count = max(1, min(count, 25))
        print(f"Getting {count} random apps from the database.")

        all_apps = db.query(models.App.id,
                            models.App.name).all()  # get all app names that are in the database, needed to check fuzzy in
        random_apps = db.query(models.App).with_entities(models.App.id, models.App.name).order_by(
            func.random()).limit(
            count).all()

        return {
            make_typo(app.name, app.id, all_apps): {"expected_appid": app.id, "expected_name": app.name}
            for app in random_apps
        }

    def register_endpoints(self, all_endpoints=False):
        """"
        Function to define all the endpoints for the API.
        """

        self.app.include_router(frontend_router)
        self.app.include_router(categories_router)

        # register routers, only when in PYCHARM or Pytest
        if os.getenv("PYCHARM_HOSTED") or os.getenv("PYTEST_RUNNING") or all_endpoints: # We dont wont users on production to modify the database with the CRUD endpoints.
            self.app.include_router(apps_router)
            self.app.include_router(categories_router_development)

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

        @self.app.get("/test", include_in_schema=False)
        def test():
            session = SessionLocal()
            fill_database(session)

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

        @self.app.get("/recommend", response_class=HTMLResponse)
        def handle_form(request: Request, game: str = "", db=self.db_dependency):
            """"
            Handle the GET request for the HTML <form> to search for a game.

            :param request: The request object auto given by FastAPI.
            :param game_input: The name or id of the game to search for. Always uses fuzzy search.
            :return: The HTML response with the results in the context.
            """
            if not game:
                return root(request, db)

            # clean up the input to prevent XSS attacks
            game_input = game.strip()
            game_input = game_input.strip()
            game_input = game_input.replace("<", "").replace(">", "")
            del game

            selected_app = app_data_from_id_or_name(game_input, db, True, True)

            #apps = [] # currently algorithm not implemented, Bram enable line below to start developing find_similar_games()
            apps = find_similar_games(selected_app, db)

            if not selected_app or not selected_app.id:
                return self.templates.TemplateResponse(
                    request=request, name="404.html", context={"message": f"Game {game_input} not found."}
                )


            nsfw = False

            for tag in selected_app.tags:
                if tag.name in BLOCKED_CONTENT_TAGS:
                    nsfw = True
                    break

            # chache the background image
            if os.getenv("CACHE_IMAGES"):
                for attr, cache_func in [("background_image", cache_background_image),
                                         ("header_image", cache_header_image)]:
                    if getattr(selected_app, attr):
                        cached = cache_func(selected_app) or {}
                        setattr(selected_app, attr, cached.get(attr, getattr(selected_app, attr)))

            return self.templates.TemplateResponse(
                request=request, name="game_output.html", context={"selected_app":selected_app, "apps": apps,"nsfw": nsfw}
            )

        def find_similar_games(selected_app, db):
            """Finds games with the most similar tags to the given game.

            :param selected_app: The app object from the DB to filter on.
            :param db: The database object
            :return: The matching games filtered on matching tags of the input "selected_app"
            """
            gameid = str(selected_app.id)
            gamename = selected_app.name

            tags = selected_app.tags
            genres = selected_app.genres
            categories = selected_app.categories

            if not tags or not genres or not categories:
                raise HTTPException(status_code=404, detail="No tags or genres or categories found for app")

            # get all games that are in the database except the selected game
            games = db.query(models.App).filter(models.App.id != selected_app.id).all()
            game_tags_relation = db.query(models.AppTags.app_id, models.AppTags.tag_id).all()

            if not games:
                raise HTTPException(status_code=404, detail="No games found in the database.")

            matching_games = []

            # Compare with every other game must be (O(n²)) (two for loops in this)
            for game in games:

                # Convert game_tags_relation to a set for faster lookups
                game_tags_relation_set = set(game_tags_relation)

                # Get tags for the current game
                game.tags = [tag for tag in tags if (game.id, tag.id) in game_tags_relation_set]

                # Calculate the similarity score based on common tags
                common_tags = set(selected_app.tags).intersection(set(game.tags))
                total_tags = len(selected_app.tags)
                game.similarity_score = ((len(common_tags) / total_tags) * 100).__round__()  # Convert to percentage

                if game.similarity_score > 0:
                    matching_games.append((game, game.similarity_score))

            # Sort matching games by similarity score in descending order
            matching_games.sort(key=lambda x: x[1], reverse=True)

            # Return the top 5 matching games
            return [game for game, _ in matching_games[:5]]

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
