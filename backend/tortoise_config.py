import os
from dotenv import load_dotenv

if os.path.exists(".env"):
    load_dotenv()
elif os.path.exists("../.env"):
    load_dotenv("../.env")

TORTOISE_CONFIG = dict(connections={
    # Dict format for connection
    'default': {
        'engine': 'tortoise.backends.asyncpg',
        'credentials': {
            'host': os.getenv("DB_HOST", "localhost"),
            'port': os.getenv("DB_PORT", "5432"),
            'user': os.getenv("DB_USER", "postgres"),
            'password': os.getenv("DB_PASS", ""),
            'database': os.getenv("DB_NAME", "fastproject"),
        }
    },
}, apps={
    'models': {
        'models': ['models', 'aerich.models'],
        # If no default_connection specified, defaults to 'default'
        'default_connection': 'default',
    }
})
