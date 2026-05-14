import os
from dotenv import load_dotenv

# Try to load .env if it exists (for local development)
# In Docker, environment variables are passed via docker-compose
if os.path.exists(".env"):
    load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Build database URL from individual components
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASS = os.getenv("DB_PASS", "postgres")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "fastproject")
    
    # Validate required fields
    if not DB_USER or not DB_PASS or not DB_NAME:
        raise ValueError(
            "Database credentials not configured. Set DATABASE_URL or provide "
            "DB_USER, DB_PASS, and DB_NAME environment variables."
        )
    
    # If inside Docker, adjust host and port if using defaults
    if os.path.exists("/.dockerenv"):
        if DB_HOST == "localhost" or DB_HOST == "127.0.0.1":
            DB_HOST = "db"
    
    DATABASE_URL = f"postgres://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Ensure localhost/127.0.0.1 are replaced in Docker context
if os.path.exists("/.dockerenv"):
    DATABASE_URL = DATABASE_URL.replace("localhost", "db").replace("127.0.0.1", "db")

print(f"Database configured: {DB_USER}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
