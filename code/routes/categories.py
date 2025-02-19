# GET requests endpoints below:
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import code.database.models as models

from code.database.database import get_db

db_dependency = Depends(get_db)

router = APIRouter()

@router.get("/tags")
def read_tags(db: Session = db_dependency):
    """"
    Get all existing tags in the database.
    :return: List of tags in JSON/dictionary format with id and name.
    """
    tags = db.query(models.Tags).all()
    return tags


@router.get("/categories")
def read_categories(db: Session = db_dependency):
    """"
    Get all existing categories in the database.
    :return: List of categories in JSON/dictionary format with id and name.
    """
    categories = db.query(models.Category).all()
    return categories


@router.get("/genres")
def read_genres(db: Session = db_dependency):
    """
    Get all existing genres in the database.
    :return: List of genres in JSON/dictionary format with id and name.
    """
    genres = db.query(models.Genre).all()
    return genres


@router.get("/cats")
def read_cats(db: Session = db_dependency):
    """
    Get all categories, genres and tags in one request.
    :return: JSON / dictionary with all existing categories, genres and tags with their id and name.
    """
    return {
        "tags": db.query(models.Tags).all(),
        "categories": db.query(models.Category).all(),
        "genres": db.query(models.Genre).all(),
    }