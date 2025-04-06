from sqlalchemy.orm import Session
from models.models import User, Request, Category
from schemas.schemas import UserCreate, RequestCreate
import json


def create_user(db: Session, user: UserCreate):
    # db_user = User(**user.dict())
    db_user = User(
        name=user.name,
        surname=user.surname,
        email=user.email,
        phone=user.phone,
        description=user.description,
        image_path=user.image_path,
        country=user.country,
        city=user.city,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_request(db: Session, req: RequestCreate):
    db_request = Request(
        name=req.name,
        description=req.description,
        image_path=req.image_path,
        state=req.state,
        id_author=req.id_author,
    )

    for cat_id in req.category_ids:
        category = db.query(Category).filter(Category.idCategories == cat_id).first()
        if category:
            db_request.categories.append(category)

    db.add(db_request)
    db.commit()
    db.refresh(db_request)

    return db_request
