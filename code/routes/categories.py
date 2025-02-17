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