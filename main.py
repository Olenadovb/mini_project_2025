"""
Server file
"""

from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, Request, Depends, UploadFile, File, Form, HTTPException
from fastapi.responses import RedirectResponse, FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials

from alembic import command
from alembic.config import Config

from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
import crud
import schemas
from config import settings
from uuid import uuid4
import shutil
import os

from pathlib import Path
from datetime import datetime
import traceback

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
async def index(request: Request):
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

models.Base.metadata.create_all(bind=engine)

UPLOAD_FOLDER = Path("static/uploads")
UPLOAD_FOLDER.mkdir(exist_ok=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}")
    return JSONResponse(status_code=500, content={"detail": str(exc)})


logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)


@app.post("/create_user")
async def create_user(
    name: str = Form(...),
    surname: str = Form(...),
    age: int = Form(...),
    country: str = Form(...),
    city: str = Form(...),
    phone: str = Form(...),
    email: str = Form(...),
    description: str = Form(...),
    categories: str = Form(...),
    photo: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    print("start")
    try:
        file_ext = os.path.splitext(photo.filename)[1]
        filename = (
            f"{email.replace('@', '_')}_{int(datetime.utcnow().timestamp())}{file_ext}"
        )
        file_path = UPLOAD_FOLDER / filename

        with open(file_path, "wb") as buffer:
            buffer.write(await photo.read())

        print("image added", file_path)
        new_user = models.User(
            name=name,
            surname=surname,
            age=age,
            country=country,
            city=city,
            phone=phone,
            email=email,
            description=description,
            image_path=str(file_path),
            created_at=datetime.utcnow(),
            categories=categories,
        )

        print("user created (before adding)")
        db.add(new_user)
        print("after adding")
        print("Поточна база:", db.bind.url)
        try:
            print("attemptig to commit...")
            db.commit()
            print("after commit (successfulS)")
        except Exception as e:
            print("❌ Помилка при коміті:", e)
            traceback.print_exc()
            db.rollback()
        # db.flush()
        print("user added")

        return JSONResponse(
            status_code=200,
            content={"message": "User created", "redirect_url": "/home"},
        )

    except Exception as e:
        print("EXCEPTION:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Server error: {e}")


@app.get("/users")
def list_users(request: Request, db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return static.TemplateResponse("users.html", {"request": request, "users": users})


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
    run_migrations()
    uvicorn.run(app, host="0.0.0.0", port=8000)
