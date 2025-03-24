"""
Server file
"""

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()


@app.get("/")
async def read_root():
    return HTMLResponse("<h1>Hello World</h1>")
