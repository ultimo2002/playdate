from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from code.database import crud
import code.database.models as models
from code.database.database import get_db

router = APIRouter()

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