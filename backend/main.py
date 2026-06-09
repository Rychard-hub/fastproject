from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise
from fastapi.staticfiles import StaticFiles
import os
from dotenv import load_dotenv
from routers import router
from shop_router import router as shop_router
from database import DATABASE_URL

if os.path.exists(".env"):
    load_dotenv()
elif os.path.exists("../.env"):
    load_dotenv("../.env")

app = FastAPI(title="FastAPI+React Blog", version="1.0")

# CORS - Allow all origins (browser requests)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(shop_router)

UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

register_tortoise(
    app,
    db_url=DATABASE_URL,
    modules={"models": ["models"]},
    generate_schemas=True,
    add_exception_handlers=True,
)

@app.get("/")
async def home():
    return {"message": "Hello World", "status": "ok"}



@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/home/shop")
async def shop_home():
    return {"message": "Shop API working"}

@app.get("/portfolio")
async def get_portfolio():
    return [
        {"title": "Project 1", "description": "FastAPI + React", "link": "https://github.com"},
        {"title": "Project 2", "description": "Blog with Tortoise ORM", "link": "https://github.com"},
        {"title": "Project 3", "description": "Dockerized architecture", "link": "https://github.com"},
        {"title": "Face exercise", "description": "Natural Wellness, Face Yoga & Exercises", "link": "#face-yoga"}
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
