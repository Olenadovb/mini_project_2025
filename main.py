"""
Server file
"""

from fastapi import FastAPI

# from fastapi.responses import HTMLResponse
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
async def home():
    return FileResponse("static/index.html")


@app.get("/categories")
async def categories():
    return FileResponse("static/categories.html")


@app.get("/profile")
async def profile():
    return FileResponse("static/profile.html")


@app.get("/settings")
async def sett():
    return FileResponse("static/settings.html")


@app.get("/aboutus")
async def about():
    return FileResponse("static/aboutus.html")
