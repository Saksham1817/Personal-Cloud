from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import users, files, photos

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Personal Cloud Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(files.router)
app.include_router(photos.router)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/apple-touch-icon.png")
def apple_icon():
    return FileResponse("static/apple-touch-icon.png")

@app.get("/apple-touch-icon-precomposed.png")
def apple_icon_pre():
    return FileResponse("static/apple-touch-icon.png")

@app.get("/favicon.ico")
def favicon():
    return FileResponse("static/favicon.ico")

@app.get("/")
def root():
    return FileResponse("static/index.html")