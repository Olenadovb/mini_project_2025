"""
Server file
"""

from fastapi.staticfiles import StaticFiles
from fastapi import (
    FastAPI,
    Request,
    # Response,
    Depends,
    UploadFile,
    File,
    Form,
    HTTPException,
    APIRouter,
    Query,
)
from fastapi.responses import RedirectResponse, FileResponse, JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.oauth2 import id_token
from googleapiclient.discovery import build
from google.auth.transport import requests

from alembic import command
from alembic.config import Config

from starlette.middleware.sessions import SessionMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from sqlalchemy.orm import Session
from server.database import SessionLocal, engine
from server import models
from server import crud
from server import schemas
from server.config import settings
from uuid import uuid4
import shutil
import os

from pathlib import Path
from datetime import datetime, timedelta
import pytz
import traceback
from typing import List, Optional

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI()
router = APIRouter()
app.include_router(router)

app.add_middleware(
    SessionMiddleware,
    secret_key="some-secret-key",
    max_age=60 * 60 * 24 * 7,
    session_cookie="session",
    https_only=False,
    same_site="lax",
)

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
static = Jinja2Templates(directory="static")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# FRONTEND

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]
REDIRECT_URI = "https://causal-joannes-olenadovb-ede57763.koyeb.app/callback"


# LOG IN / SIGN IN


def get_current_user(request: Request, db: Session = Depends(get_db)):
    print("SESSION:", request.session)
    user_id = request.session.get("user_id")
    user_email = request.session.get("user_email")
    if user_id and user_email:
        user = db.query(models.User).filter(models.User.idUsers == user_id).first()
        if user:
            return user
    raise HTTPException(status_code=401, detail="Unauthorized")


def admin_required(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if current_user.email != settings.admin_email:
        raise HTTPException(status_code=403, detail="Access denied - Admins only")
    return current_user


@app.get("/login")
async def login():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, redirect_uri=REDIRECT_URI
    )
    auth_url, state = flow.authorization_url(prompt="consent")
    return RedirectResponse(auth_url)


@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=302)


@app.get("/callback")
async def callback(request: Request, db: Session = Depends(get_db)):
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, redirect_uri=REDIRECT_URI
    )
    flow.fetch_token(authorization_response=str(request.url))
    credentials = flow.credentials
    id_info = id_token.verify_oauth2_token(
        credentials.id_token, requests.Request(), audience=None
    )
    user_email = id_info["email"]
    request.session["user_email"] = user_email
    user = db.query(models.User).filter(models.User.email == user_email).first()

    if user:
        request.session["user_id"] = user.idUsers
        print("Set session before redirect:", request.session)
        return RedirectResponse(url="/home")
    return RedirectResponse(url="/create_profile")


@app.get("/create_profile", response_class=FileResponse)
async def create_pr(request: Request):
    # return FileResponse("static/create_pr.html")
    return static.TemplateResponse("create_profile.html", {"request": request})


@app.get("/add_request", response_class=FileResponse)
async def create_req(request: Request):
    # return FileResponse("static/create_pr.html")
    return static.TemplateResponse("create_request.html", {"request": request})


@app.get("/go_edit_profile", response_class=HTMLResponse)
async def get_edit_profile(
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    user = (
        db.query(models.User)
        .filter(models.User.idUsers == current_user.idUsers)
        .first()
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return static.TemplateResponse(
        "edit_profile.html", {"request": request, "user": user}
    )


@app.post("/edit_profile")
async def post_edit_profile(
    name: str = Form(...),
    surname: str = Form(...),
    age: int = Form(...),
    country: str = Form(...),
    city: str = Form(...),
    phone: str = Form(...),
    description: str = Form(...),
    categories: str = Form(...),
    photo: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    print(
        "Received:", name, surname, age, country, city, phone, description, categories
    )
    user = (
        db.query(models.User)
        .filter(models.User.idUsers == current_user.idUsers)
        .first()
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.name = name
    user.surname = surname
    user.age = age
    user.country = country
    user.city = city
    user.phone = phone
    user.description = description
    user.categories = categories

    if photo:
        uploads_dir = "static/uploads"
        os.makedirs(uploads_dir, exist_ok=True)
        filename = f"user_{user.idUsers}_{photo.filename}"
        file_path = os.path.join(uploads_dir, filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(photo.file, buffer)
        user.photo = file_path

    db.commit()
    db.refresh(user)

    return JSONResponse(
        status_code=200,
        content={
            "message": "Profile updated successfully",
            "redirect_url": "/profile",
        },
    )


@app.post("/request/{req_id}/change_status")
async def change_status(
    req_id: int,
    new_status: int = Form(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    activity = (
        db.query(models.Request)
        .filter_by(idRequests=req_id, id_author=current_user.idUsers)
        .first()
    )
    if not activity:
        return RedirectResponse(url="/error", status_code=303)

    activity.state = new_status
    db.commit()

    print("State updated successfully", activity.state)
    return RedirectResponse(url="/profile", status_code=302)


# DATABASE

# models.Base.metadata.drop_all(bind=engine)
# models.Base.metadata.create_all(bind=engine)

UPLOAD_FOLDER = Path("static/uploads")
UPLOAD_FOLDER.mkdir(exist_ok=True)


logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)


# DATABASE WRITE


@app.post("/create_user")
async def create_user(
    request: Request,
    name: str = Form(...),
    surname: str = Form(...),
    age: int = Form(...),
    country: str = Form(...),
    city: str = Form(...),
    phone: str = Form(...),
    description: str = Form(...),
    categories: str = Form(...),
    photo: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    user_email = request.session.get("user_email")
    if not user_email:
        # raise HTTPException(status_code=401, detail="Not authenticated")
        return RedirectResponse(url="/error", status_code=401)
    # print("start")
    file_ext = os.path.splitext(photo.filename)[1]
    filename = (
        f"{user_email.replace('@', '_')}_{int(datetime.utcnow().timestamp())}{file_ext}"
    )
    file_path = UPLOAD_FOLDER / filename

    with open(file_path, "wb") as buffer:
        buffer.write(await photo.read())

    # local_tz = pytz.timezone("Europe/Kyiv")
    # print("image added", file_path)
    new_user = models.User(
        name=name,
        surname=surname,
        age=age,
        country=country,
        city=city,
        phone=phone,
        email=user_email,
        description=description,
        image_path=str(file_path),
        created_at=datetime.utcnow(),
        categories=categories,
    )

    # print("user created (before adding)")
    db.add(new_user)
    # print("after adding")
    db.commit()
    db.refresh(new_user)
    # print("user added")
    request.session["user_email"] = new_user.email
    request.session["user_id"] = new_user.idUsers

    return JSONResponse(
        status_code=200,
        content={"message": "User created", "redirect_url": "/home"},
    )


@app.post("/create_request")
async def create_request(
    request: Request,
    name: str = Form(...),
    description: str = Form(...),
    state: int = Form(...),
    categories: str = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    user_email = request.session.get("user_email")
    if not user_email:
        return RedirectResponse(url="/error", status_code=401)

    user = db.query(models.User).filter_by(email=user_email).first()
    if not user:
        return RedirectResponse(url="/error", status_code=401)

    file_ext = os.path.splitext(image.filename)[1]
    filename = f"req_{uuid4().hex}{file_ext}"
    file_path = UPLOAD_FOLDER / filename
    with open(file_path, "wb") as buffer:
        buffer.write(await image.read())

    new_request = models.Request(
        name=name,
        description=description,
        image_path=str(file_path),
        created_at=datetime.utcnow(),
        state=state,
        id_author=user.idUsers,
        categories=categories.strip(),
    )

    db.add(new_request)
    db.commit()

    return JSONResponse(
        status_code=200,
        content={"message": "Request created", "redirect_url": "/profile"},
    )


# DATABASE READ

@app.get("/admin")
def list_users(
    request: Request,
    db: Session = Depends(get_db),
    admin: models.User = Depends(admin_required),
):
    users = db.query(models.User).all()
    return static.TemplateResponse("users.html", {"request": request, "users": users})


@app.get("/categories")
def show_categories(
    request: Request,
    category: Optional[List[str]] = Query(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    user = (
        db.query(models.User)
        .filter(models.User.idUsers == current_user.idUsers)
        .first()
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    all_requests = db.query(models.Request).all()
    if category:

        def matches_categories(req: models.Request):
            req_cats = [c.strip() for c in req.categories.split(",")]
            return any(c in req_cats for c in category)

        filtered_requests = [req for req in all_requests if matches_categories(req)]
    else:
        filtered_requests = all_requests
    return static.TemplateResponse(
        "categories.html",
        {
            "request": request,
            "requests": filtered_requests,
            "selected_categories": category,
        },
    )


@app.get("/", response_class=HTMLResponse)
def get_activity(
    request: Request,
    db: Session = Depends(get_db),
):
    # logger.info(f"Session data: {request.session}")
    user = request.session.get("user_email")
    if user:
        return RedirectResponse(url="/home", status_code=302)
    recent_requests = (
        db.query(models.Request, models.User)
        # .join(models.User, models.User.idUsers == models.Request.id_author)
        .order_by(models.Request.created_at.desc())
        .limit(5)
        .all()
    )
    activities = []
    for req, user in recent_requests:
        activities.append(
            {
                "name": user.name,
                "surname": user.surname,
                "description": req.description,
                "image_path": (
                    req.image_path if req.image_path else "/static/default_avatar.jpg"
                ),
                "time": req.created_at,
            }
        )
    return static.TemplateResponse(
        "index.html", {"request": request, "activities": activities}
    )


@app.get("/home", response_class=HTMLResponse)
def home_request(
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    recent_requests = (
        db.query(models.Request, models.User)
        .join(models.User, models.User.idUsers == models.Request.id_author)
        # .filter(models.Request.state != 3)
        .order_by(models.Request.created_at.desc())
        .limit(2)
        .all()
    )
    user = (
        db.query(models.User)
        .filter(models.User.idUsers == current_user.idUsers)
        .first()
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    activities = []
    for req, user in recent_requests:
        activities.append(
            {
                "firstname": user.name,
                "surname": user.surname,
                "name": req.name,
                "categories": req.categories,
                "description": req.description,
                "image_path": (
                    req.image_path if req.image_path else "/static/default_avatar.jpg"
                ),
                "time": req.created_at,
            }
        )
    print("Session in /home:", request.session)
    return static.TemplateResponse(
        "home.html", {"request": request, "activities": activities}
    )


@app.get("/profile", response_class=HTMLResponse)
def profile(
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    user = (
        db.query(models.User)
        .filter(models.User.idUsers == current_user.idUsers)
        .first()
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user_requests = (
        db.query(models.Request)
        .filter(models.Request.id_author == current_user.idUsers)
        .order_by(models.Request.created_at.desc())
        .all()
    )
    activities = [
        {
            "name": req.name,
            "categories": req.categories,
            "description": req.description,
            "image_path": (
                req.image_path if req.image_path else "/static/default_avatar.jpg"
            ),
            "time": req.created_at,
            "req_id": req.idRequests,
            "state": req.state,
        }
        for req in user_requests
    ]
    return static.TemplateResponse(
        "profile.html", {"request": request, "user": user, "activities": activities}
    )


@app.get("/request/{request_id}", response_class=HTMLResponse)
async def view_request(
    request: Request,
    request_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    user = (
        db.query(models.User)
        .filter(models.User.idUsers == current_user.idUsers)
        .first()
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db_request = (
        db.query(models.Request)
        .filter(models.Request.idRequests == int(request_id))
        .first()
    )
    if not db_request:
        raise HTTPException(status_code=404, detail="Request not found")
    author = (
        db.query(models.User)
        .filter(models.User.idUsers == db_request.id_author)
        .first()
    )
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    return static.TemplateResponse(
        "request.html",
        {
            "request": request,
            "request_data": db_request,
            "author": author,
        },
    )


@app.get("/user/{user_id}", response_class=HTMLResponse)
async def view_user(
    request: Request,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    user = db.query(models.User).filter(models.User.idUsers == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user_requests = (
        db.query(models.Request)
        .filter(models.Request.id_author == user.idUsers)
        .order_by(models.Request.created_at.desc())
        .all()
    )
    activities = [
        {
            "name": req.name,
            "categories": req.categories,
            "description": req.description,
            "image_path": (
                req.image_path if req.image_path else "/static/default_avatar.jpg"
            ),
            "time": req.created_at,
            "req_id": req.idRequests,
        }
        for req in user_requests
    ]
    if current_user.idUsers == user_id:
        return RedirectResponse(url="/profile", status_code=302)
    return static.TemplateResponse(
        "user.html", {"request": request, "user": user, "activities": activities}
    )


@app.get("/aboutus")
async def aboutus(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    user = (
        db.query(models.User)
        .filter(models.User.idUsers == current_user.idUsers)
        .first()
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return FileResponse("static/aboutus.html")


@app.get("/registrate")
async def registrate():
    return FileResponse("static/registration.html")


# ERROR HANDLING


@app.get("/error")
async def error(request: Request, status_code: int):
    detail = ""
    return static.TemplateResponse(
        "error.html",
        {"request": request, "status_code": status_code, "status_text": detail},
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.error(f"HTTPException: {exc.status_code} - {exc.detail}")
    return static.TemplateResponse(
        "error.html",
        {"request": request, "status_code": exc.status_code, "status_text": exc.detail},
        status_code=exc.status_code,
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled Exception: {repr(exc)}")
    return static.TemplateResponse(
        "error.html",
        {
            "request": request,
            "status_code": 500,
            "status_text": "Internal Server Error",
        },
        status_code=500,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation Error: {exc}")
    return static.TemplateResponse(
        "error.html",
        {"request": request, "status_code": 422, "status_text": "Validation Error"},
        status_code=422,
    )


# DATABASE MIGRATIONS


def run_migrations():
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")


if __name__ == "__main__":
    import uvicorn

    run_migrations()
    uvicorn.run(app, host="0.0.0.0", port=8000)
