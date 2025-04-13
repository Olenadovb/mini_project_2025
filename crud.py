from sqlalchemy.orm import Session
from models import User, Request, Category
from schemas import UserCreate, RequestCreate
from fastapi import UploadFile, File
from datetime import datetime
import json


def create_user(
    db: Session,
    name: str,
    surname: str,
    age: int,
    country: str,
    city: str,
    phone: str,
    email: str,
    description: str,
    image_path: str,
    categories: str,
    created_at=None,
):
    db_user = User(
        name=name,
        surname=surname,
        age=age,
        country=country,
        city=city,
        phone=phone,
        email=email,
        description=description,
        image_path=image_path,
        categories=categories,
        created_at=created_at or datetime.utcnow(),
    )
    # db.add(db_user)
    # db.commit()
    # db.refresh(db_user)
    # return db_user
    try:
        print("...adding user to DB:", db_user)
        db.add(db_user)
        db.commit()
        print("Committed to DB")
        db.refresh(db_user)
        print("Refreshed from DB")
        print("user saved to db", db_user)
        # db.flush()
        # print("Flushed successfully")
        return db_user
    except Exception as e:
        db.rollback()
        print("❌ CRUD error:", e)
        raise e


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
