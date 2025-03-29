"""
Server file
"""

from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, Request, Depends
from fastapi.responses import RedirectResponse, FileResponse
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from fastapi.templating import Jinja2Templates
import os

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
app = FastAPI()
static = Jinja2Templates(directory="static")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]
REDIRECT_URI = "http://localhost:8000/callback"

flow = Flow.from_client_secrets_file(
    CLIENT_SECRETS_FILE, scopes=SCOPES, redirect_uri=REDIRECT_URI
)


@app.get("/")
async def home(request: Request):
    # return FileResponse("static/index.html")
    return static.TemplateResponse("index.html", {"request": request})


@app.get("/categories")
async def categories():
    return FileResponse("static/categories.html")


@app.get("/registrate")
async def registrate():
    return FileResponse("static/registration.html")


@app.get("/login")
async def login():
    auth_url, state = flow.authorization_url(prompt="consent")
    return RedirectResponse(auth_url)


@app.get("/callback")
async def callback(request: Request):
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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
