from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

def get_all(db: Session, model):
    return db.query(model).all()

def get_by_id(db: Session, model, record_id: int):
    return db.query(model).filter(model.id == record_id).first()

def create(db: Session, model, **kwargs):
    new_record = model(**kwargs)
    db.add(new_record)
    try:
        db.commit()
        db.refresh(new_record)
        return new_record
    except IntegrityError:
        db.rollback()
        return None  # Handle duplicate errors, if needed

def update(db: Session, model, record_id: int, **kwargs):
    record = db.query(model).filter(model.id == record_id).first()
    if not record:
        return None
    for key, value in kwargs.items():
        if value is not None:  # Only update non-null values
            setattr(record, key, value)
    db.commit()
    return record

def delete(db: Session, model, record_id: int):
    record = db.query(model).filter(model.id == record_id).first()
    if record:
        db.delete(record)
        db.commit()
        return record
    return None

def handle_update(db: Session, model, id: int, name: str):
    record = update(db, model, id, name=name)
    if record is None:
        raise HTTPException(status_code=404, detail=f"{model.__name__} {id} not found")
    return record

def handle_delete(db: Session, model, id: int):
    record = delete(db, model, id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"{model.__name__} {id} not found")
    return {"message": f"{model.__name__} deleted successfully"}