from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise
from fastapi.staticfiles import StaticFiles
import os
from dotenv import load_dotenv
from routers import router
from shop_router import router as shop_router
from r2_router import router as r2_router
from database import DATABASE_URL

load_dotenv()

def validate_environment():
    """Validate that required environment variables are set."""
    required_vars = {
        "DB_USER": "Database user",
        "DB_PASS": "Database password",
        "DB_NAME": "Database name",
    }
    
    optional_but_recommended = {
        "STRIPE_SECRET_KEY": "Stripe API key (required for shop functionality)",
    }
    
    missing_required = []
    for var, description in required_vars.items():
        if not os.getenv(var) and not os.getenv("DATABASE_URL"):
            missing_required.append(f"{var} ({description})")
    
    missing_optional = []
    for var, description in optional_but_recommended.items():
        if not os.getenv(var):
            missing_optional.append(f"{var} ({description})")
    
    if missing_required:
        raise ValueError(
            f"Missing required environment variables:\n" + "\n".join(missing_required)
        )
    
    if missing_optional:
        print(f"WARNING: Missing optional environment variables:\n" + "\n".join(missing_optional))

# Validate environment before creating app
validate_environment()

UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

app = FastAPI(
    title="FastAPI+React Blog",
    description="Blog system with Tortoise ORM and Aerich",
    version="1.0",
) 

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(shop_router)
app.include_router(r2_router)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

register_tortoise(
    app,
    config=None,
    config_file=None,
    db_url=DATABASE_URL,
    modules={"models": ["models"]},
    generate_schemas=True,
    add_exception_handlers=True,
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
async def home():
    return {
        "message": "Hello!! My Lord is World",
        "r2_public_domain": os.getenv("R2_PUBLIC_DOMAIN"),
        "r2_bucket_name": os.getenv("R2_BUCKET_NAME")
    }

@app.get("/portfolio")
async def get_portfolio():
    return [
        {
            "title": "Project 1",
            "description": "FastAPI + React application showcasing portfolio items.",
            "link": "https://github.com"
        },
        {
            "title": "Project 2",
            "description": "A database-driven blog system using Tortoise ORM.",
            "link": "https://github.com"
        },
        {
            "title": "Project 3",
            "description": "Dockerized microservices architecture.",
            "link": "https://github.com"
        }
    ]

@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
