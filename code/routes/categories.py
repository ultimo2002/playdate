from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

import code.database.models as models
from code.database.crud import handle_update, handle_delete
from code.database.database import get_db

router = APIRouter()

@router.put("/category/", response_model=dict)
def update_category(id: int, name: str = Query(None), db: Session = Depends(get_db)):
    return handle_update(db, models.Category, id, name)

@router.delete("/category/{id}", response_model=dict)
def delete_category(id: int, db: Session = Depends(get_db)):
    return handle_delete(db, models.Category, id)

@router.put("/genre/", response_model=dict)
def update_genre(id: int, name: str = Query(None), db: Session = Depends(get_db)):
    return handle_update(db, models.Genre, id, name)

@router.delete("/genre/{id}", response_model=dict)
def delete_genre(id: int, db: Session = Depends(get_db)):
    return handle_delete(db, models.Genre, id)

@router.put("/tag/", response_model=dict)
def update_tag(id: int, name: str = Query(None), db: Session = Depends(get_db)):
    return handle_update(db, models.Tags, id, name)

@router.delete("/tag/{id}", response_model=dict)
def delete_tag(id: int, db: Session = Depends(get_db)):
    return handle_delete(db, models.Tags, id)


@router.get("/tags")
def read_tags(db: Session = Depends(get_db)):
    """"
    Get all existing tags in the database.
    :return: List of tags in JSON/dictionary format with id and name.
    """
    tags = db.query(models.Tags).all()
    return tags


@router.get("/categories")
def read_categories(db: Session = Depends(get_db)):
    """"
    Get all existing categories in the database.
    :return: List of categories in JSON/dictionary format with id and name.
    """
    categories = db.query(models.Category).all()
    return categories


@router.get("/genres")
def read_genres(db: Session = Depends(get_db)):
    """
    Get all existing genres in the database.
    :return: List of genres in JSON/dictionary format with id and name.
    """
    genres = db.query(models.Genre).all()
    return genres


@router.get("/cats")
def read_cats(db: Session = Depends(get_db)):
    """
    Get all categories, genres and tags in one request.
    :return: JSON / dictionary with all existing categories, genres and tags with their id and name.
    """
    return {
        "tags": db.query(models.Tags).all(),
        "categories": db.query(models.Category).all(),
        "genres": db.query(models.Genre).all(),
    }