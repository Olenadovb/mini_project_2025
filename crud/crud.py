from sqlalchemy.orm import Session
from models.models import User, Request, Category
from schemas.schemas import UserCreate, RequestCreate
from fastapi import UploadFile, File
from datetime import datetime
import json


def create_user(
    db: Session,
    name: str,
    surname: str,
    email: str,
    phone: str,
    description: str,
    image_path: str,
    country: str,
    city: str,
    created_at=None,
):
    db_user = User(
        name=name,
        surname=surname,
        email=email,
        phone=phone,
        description=description,
        image_path=image_path,
        country=country,
        city=city,
        created_at=created_at or datetime.utcnow(),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# def create_user(db: Session, user: UserCreate):
#     # db_user = User(**user.dict())
#     db_user = User(
#         name=user.name,
#         surname=user.surname,
#         email=user.email,
#         phone=user.phone,
#         description=user.description,
#         image_path=user.image_path,
#         country=user.country,
#         city=user.city,
#         created_at=user.created_at or datetime.utcnow(),
#     )
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
#     print(db.query(User).filter_by(email=user.email).first())
#     return db_user


def create_request(db: Session, req: RequestCreate, image: UploadFile = File(...)):
    image_path = f"uploads/{image.filename}"

    with open(image_path, "wb") as f:
        f.write(image.file.read())

    db_request = Request(
        name=req.name,
        description=req.description,
        image_path=image_path,
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


# def create_request(db: Session, req: RequestCreate):
#     db_request = Request(
#         name=req.name,
#         description=req.description,
#         image_path=req.image_path,
#         state=req.state,
#         id_author=req.id_author,
#     )

#     for cat_id in req.category_ids:
#         category = db.query(Category).filter(Category.idCategories == cat_id).first()
#         if category:
#             db_request.categories.append(category)

#     db.add(db_request)
#     db.commit()
#     db.refresh(db_request)

#     return db_request
