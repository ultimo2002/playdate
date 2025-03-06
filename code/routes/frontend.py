import os
import re

from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from sqlalchemy.sql import exists
from sqlalchemy.sql.expression import func

import code.database.models as models
from code.algoritmes.cache import cache_background_image, cache_header_image
from code.config import BLOCKED_CONTENT_TAGS
from code.database.database import get_db
from code.routes.development.apps import app_data_from_id_or_name

templates = Jinja2Templates(directory="code/templates")

router = APIRouter()

db_dependency = Depends(get_db)

# The endpoints defined in this file are accessible for everyone.
# Not only in development mode. Unlike the other routers in app.py and categories.py

@router.get("/", response_class=HTMLResponse)
def root(request: Request, db=db_dependency):
    """"
    The root endpoint of the API when visiting the website.
    :return: The HTML response from the index.html template.
    """

    # Get a random background_image from the database
    background_image = (
        db.query(models.App.background_image, models.App.id, models.App.name)
        .filter(
            ~exists().where(
                (models.AppTags.app_id == models.App.id) &
                (models.AppTags.tag_id == models.Tags.id) &
                (models.Tags.name.in_(BLOCKED_CONTENT_TAGS))
            )
        )
        .order_by(func.random())
        .limit(1)
        .first()
    )
    try:
        background_image = background_image if background_image else None
    except (TypeError, IndexError, KeyError):
        background_image = None

    if os.getenv("CACHE_IMAGES") and background_image:
        background_image = cache_background_image(background_image)


    return templates.TemplateResponse(
        request=request, name="index.html",
        context={"message": "", "background_image": background_image}
    )


@router.get("/recommend", response_class=HTMLResponse)
def handle_form(request: Request, games: str = "", amount: int = 5, db=db_dependency):
    """"
    Handle the GET request for the HTML <form> to search for a game.

    :param request: The request object auto given by FastAPI.
    :param game_input: The name or id of the game to search for. Always uses fuzzy search.
    :return: The HTML response with the results in the context.
    """
    if not games:
        return root(request, db)

    # limit amount by min 1 and max 10
    amount = max(1, min(amount, 10))

    return templates.TemplateResponse(
        request=request, name="game_output.html", context=get_recommendations_games(games, db, amount)
    )

@router.get("/recommendations")
def get_recommendations_games(games: str = "", db=db_dependency, amount: int = 5):
    """"
    Get all the recommendations for the selected games.
    :param selected_games: The selected games to get recommendations for.
    :param db: The database object.
    :return: A list of recommended games.
    """
    selected_apps = []
    recommended_apps = {}
    nsfw = False

    if type(games) == str:
        games = games.split(",")

    for gameid in games:
        gameid = str(gameid.strip())

        selected_app = app_data_from_id_or_name(gameid, db, True, True)
        selected_apps.append(selected_app.__dict__)

        apps = find_similar_games(selected_app, db, amount)

        if not selected_app.id:
            raise HTTPException(status_code=404, detail=f"Game {selected_app.id} not found.")

        for tag in selected_app.tags:
            if tag.name in BLOCKED_CONTENT_TAGS:
                nsfw = True
                break

        recommended_apps[re.sub(r'[^a-zA-Z0-9 ]', '', selected_app.name)] = apps


    return {"selected_games": selected_apps, "all_apps": recommended_apps, "nsfw": nsfw}

def find_similar_games(selected_app, db, amount):
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
        try:
            game.similarity_score = ((len(common_tags) / total_tags) * 100).__round__()  # Convert to percentage
        except ZeroDivisionError:
            game.similarity_score = 0

        if game.similarity_score > 0:
            matching_games.append((game.__dict__, game.similarity_score))

    # Sort matching games by similarity score in descending order
    matching_games.sort(key=lambda x: x[1], reverse=True)

    # Return the top 5 matching games.
    return [game for game, _ in matching_games[:amount]]
