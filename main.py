"""
Server file
"""

from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, Request, Depends, UploadFile, File, Form
from fastapi.responses import RedirectResponse, FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials

from alembic import command
from alembic.config import Config

from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import models
from crud import crud
from schemas import schemas
from config import settings
from uuid import uuid4
import shutil
import os

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI()

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
static = Jinja2Templates(directory="static")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")


# FRONTEND

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]
REDIRECT_URI = "http://localhost:8000/callback"


@app.get("/")
async def home(request: Request):
    # return FileResponse("static/index.html")
    return static.TemplateResponse("index.html", {"request": request})


@app.get("/home")
async def home():
    return FileResponse("static/home.html")


@app.get("/categories")
async def categories():
    return FileResponse("static/categories.html")


@app.get("/settings")
async def settings_page():
    return FileResponse("static/settings.html")


@app.get("/profile")
async def profile():
    return FileResponse("static/profile.html")


@app.get("/aboutus")
async def aboutus():
    return FileResponse("static/aboutus.html")


@app.get("/registrate")
async def registrate():
    return FileResponse("static/registration.html")


@app.get("/login")
async def login():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, redirect_uri=REDIRECT_URI
    )
    auth_url, state = flow.authorization_url(prompt="consent")
    return RedirectResponse(auth_url)


@app.get("/callback")
async def callback(request: Request):
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, redirect_uri=REDIRECT_URI
    )
    flow.fetch_token(authorization_response=str(request.url))
    credentials = flow.credentials
    return RedirectResponse(url="/create_profile")


@app.get("/create_profile", response_class=FileResponse)
async def create_pr(request: Request):
    # return FileResponse("static/create_pr.html")
    return static.TemplateResponse("create_profile.html", {"request": request})


# @app.get("/welcome", response_class=FileResponse)
# async def welcome(request: Request):
#     return static.TemplateResponse("welcome.html", {"request": request})


# DATABASE

# models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# @app.post("/create_user", response_model=schemas.UserResponse)
# async def create_user(formData: schemas.UserCreate, db: Session = Depends(get_db)):
#     user = crud.create_user(db, formData)
#     logger.info(f"User created: {user.name} {user.surname}, ID: {user.idUsers}")
#     return {"message": "User registered successfully"}


@app.post("/create_user")
async def create_user(
    name: str = Form(...),
    surname: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    description: str = Form(...),
    country: str = Form(...),
    city: str = Form(...),
    photo: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    uploads_dir = "static/uploads"
    os.makedirs(uploads_dir, exist_ok=True)
    filename = f"{uuid4().hex}_{photo.filename}"
    file_path = os.path.join(uploads_dir, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(photo.file, buffer)

    image_path = f"/{file_path}"

    user = crud.create_user(
        db=db,
        name=name,
        surname=surname,
        email=email,
        phone=phone,
        description=description,
        image_path=image_path,
        country=country,
        city=city,
    )
    return RedirectResponse(url="/home", status_code=303)
    # return {"message": "User created", "user_id": user.idUsers}


# def create_new_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
#     return crud.create_user(db, user)


@app.post("/requests", response_model=schemas.RequestResponse)
def create_new_request(req: schemas.RequestCreate, db: Session = Depends(get_db)):
    return crud.create_request(db, req)


@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()


# DATABASE

# models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# @app.post("/create_user", response_model=schemas.UserResponse)
# async def create_user(formData: schemas.UserCreate, db: Session = Depends(get_db)):
#     user = crud.create_user(db, formData)
#     logger.info(f"User created: {user.name} {user.surname}, ID: {user.idUsers}")
#     return {"message": "User registered successfully"}


@app.post("/create_user")
async def create_user(
    name: str = Form(...),
    surname: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    description: str = Form(...),
    country: str = Form(...),
    city: str = Form(...),
    photo: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    uploads_dir = "static/uploads"
    os.makedirs(uploads_dir, exist_ok=True)
    filename = f"{uuid4().hex}_{photo.filename}"
    file_path = os.path.join(uploads_dir, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(photo.file, buffer)

    image_path = f"/{file_path}"

    user = crud.create_user(
        db=db,
        name=name,
        surname=surname,
        email=email,
        phone=phone,
        description=description,
        image_path=image_path,
        country=country,
        city=city,
    )
    return RedirectResponse(url="/home", status_code=303)
    # return {"message": "User created", "user_id": user.idUsers}


# def create_new_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
#     return crud.create_user(db, user)


@app.post("/requests", response_model=schemas.RequestResponse)
def create_new_request(req: schemas.RequestCreate, db: Session = Depends(get_db)):
    return crud.create_request(db, req)


@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()


# DATABASE MIGRATIONS


def run_migrations():
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
