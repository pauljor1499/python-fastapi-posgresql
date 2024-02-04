from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from typing import List

DB_USERNAME = 'admin'
DB_PASSWORD = 'admin'
DB_HOST = '127.0.0.1'
DB_PORT = '5432'
DB_NAME = 'Project1'

# Update the database URL for PostgreSQL
DATABASE_URL = "postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
Base = declarative_base()

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

# FastAPI setup
app = FastAPI()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# CRUD operations
def create_item(db: Session, item: Item):
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

def get_items(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Item).offset(skip).limit(limit).all()

def get_item(db: Session, item_id: int):
    return db.query(Item).filter(Item.id == item_id).first()

def update_item(db: Session, item_id: int, new_data: dict):
    item = db.query(Item).filter(Item.id == item_id).first()
    for key, value in new_data.items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item

def delete_item(db: Session, item_id: int):
    item = db.query(Item).filter(Item.id == item_id).first()
    db.delete(item)
    db.commit()
    return item

# Routes
@app.post("/items/", response_model=Item)
def create_item_api(item: Item, db: Session = Depends(get_db)):
    return create_item(db, item)

@app.get("/items/", response_model=List[Item])
def read_items(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return get_items(db, skip=skip, limit=limit)

@app.get("/items/{item_id}", response_model=Item)
def read_item(item_id: int, db: Session = Depends(get_db)):
    return get_item(db, item_id)

@app.put("/items/{item_id}", response_model=Item)
def update_item_api(item_id: int, new_data: dict, db: Session = Depends(get_db)):
    return update_item(db, item_id, new_data)

@app.delete("/items/{item_id}", response_model=Item)
def delete_item_api(item_id: int, db: Session = Depends(get_db)):
    return delete_item(db, item_id)
