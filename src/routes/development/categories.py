from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

import src.database.models as models
from src.database.crud import handle_update, handle_delete, handle_create
from src.database.database import get_db

router_development = APIRouter()

db_dependency = Depends(get_db)

# The endpoints defined in this file are only accessible when run in development.
# (E.g Executed in PyCharm)

@router_development.put("/category/", response_model=dict)
def update_category(id: int, name: str = Query(None), db: Session = db_dependency):
    return handle_update(db, models.Category, id, name)

@router_development.delete("/category/{id}", response_model=dict)
def delete_category(id: int, db: Session = db_dependency):
    return handle_delete(db, models.Category, id)

@router_development.post("/category/", response_model=dict)
def create_category(id: int, name: str, db: Session = db_dependency):
    return handle_create(db, models.Category, id=id, name=name)

@router_development.put("/genre/", response_model=dict)
def update_genre(id: int, name: str = Query(None), db: Session = db_dependency):
    return handle_update(db, models.Genre, id, name)

@router_development.delete("/genre/{id}", response_model=dict)
def delete_genre(id: int, db: Session = db_dependency):
    return handle_delete(db, models.Genre, id)

@router_development.post("/genre/", response_model=dict)
def create_genre(id: int, name: str, db: Session = db_dependency):
    return handle_create(db, models.Genre, id=id, name=name)

@router_development.put("/tag/", response_model=dict)
def update_tag(id: int, name: str = Query(None), db: Session = db_dependency):
    return handle_update(db, models.Tags, id, name)

@router_development.delete("/tag/{id}", response_model=dict)
def delete_tag(id: int, db: Session = db_dependency):
    return handle_delete(db, models.Tags, id)

@router_development.post("/tag/", response_model=dict)
def create_tag(id: int, name: str, db: Session = db_dependency):
    return handle_create(db, models.Tags, id=id, name=name)