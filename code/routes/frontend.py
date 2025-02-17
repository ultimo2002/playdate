import os

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from sqlalchemy.sql import exists
from sqlalchemy.sql.expression import func

import code.database.models as models
from code.algoritmes.cache import cache_background_image, cache_header_image
from code.config import BLOCKED_CONTENT_TAGS
from code.database.database import get_db
from code.routes.apps import app_data_from_id_or_name

templates = Jinja2Templates(directory="code/templates")

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
def root(request: Request, db=Depends(get_db)):
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
def handle_form(request: Request, game: str = "", db=Depends(get_db)):
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

    apps = []  # currently algorithm not implemented, Bram enable line below to start developing find_similar_games()
    # apps = find_similar_games(selected_app, db)

    if not selected_app or not selected_app.id:
        return templates.TemplateResponse(
            request=request, name="404.html", context={"message": f"Game {game_input} not found."}
        )

    nsfw = False

    for tag in selected_app.tags:
        if tag.name in BLOCKED_CONTENT_TAGS:
            nsfw = True
            break

    # chache the background image
    if os.getenv("CACHE_IMAGES"):
        if selected_app.background_image:
            cached = cache_background_image(selected_app)
            try:
                selected_app.background_image = cached["background_image"] if cached else selected_app.background_image
            except (TypeError, KeyError):
                selected_app.background_image = selected_app.background_image

        if selected_app.header_image:
            cached = cache_header_image(selected_app)
            try:
                selected_app.header_image = cached["header_image"] if cached else selected_app.header_image
            except (TypeError, KeyError):
                selected_app.header_image = selected_app.header_image

    return templates.TemplateResponse(
        request=request, name="game_output.html", context={"selected_app": selected_app, "apps": apps, "nsfw": nsfw}
    )