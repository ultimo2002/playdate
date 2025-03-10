from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.algoritmes.fuzzy import _most_similar
from src.database import crud
import src.database.models as models
from src.database.database import get_db

router = APIRouter()

# The endpoints defined in this file are only accessible when run in development.
# (E.g Executed in PyCharm)

@router.put("/app/", response_model=dict)
def update_app(
    item_id: int,
    name: str = Query(None),
    description: str = Query(None),
    developer: str = Query(None),
    header_image: str = Query(None),
    background_image: str = Query(None),
    price: str = Query(None),
    db: Session = Depends(get_db)
):
    item = crud.update(db, models.App, item_id, name=name, description=description, developer=developer, header_image=header_image, background_image=background_image, price=price)
    if item is None:
        raise HTTPException(status_code=404, detail=f"App {item_id} not found")
    return item

@router.delete("/app/{item_id}", response_model=dict)
def delete_app(item_id: int, db: Session = Depends(get_db)):
    app = crud.delete(db, models.App, item_id)
    if app is None:
        raise HTTPException(status_code=404, detail=f"App {app} not found")
    return {"message": "App deleted successfully"}

@router.post("/app/")
def create_app(
    name: str,
    description: str,
    developer: str,
    header_image: str,
    background_image: str,
    price: str,
    db: Session = Depends(get_db)
    ):
    return crud.create(db, models.App, name=name, description=description, developer=developer, header_image=header_image, background_image=background_image, price=price)

def most_similar_named_app(target_name: str, db):
    """
    Helper function to find the most similar named app in the database.

    :param target_name: The name of the app to find the most similar named app for.
    :param db: The database dependency.
    :return: Dictionary / JSON with the (id, name and similarity) of the app.
    """
    apps = db.query(models.App).with_entities(models.App.id, models.App.name).all()
    most_similar_app, similarity = _most_similar(target_name, apps, "name")

    if most_similar_app:
        return {"id": most_similar_app.id, "name": most_similar_app.name, "similarity": similarity}

    return None

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
                print(
                    f"Most similar app for '{app_id_or_name}' is '{similar_app['name']}' with similarity: {similar_app['similarity']}")
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