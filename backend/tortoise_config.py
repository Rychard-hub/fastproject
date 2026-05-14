TORTOISE_CONFIG = dict(connections={
    # Dict format for connection
    'default': {
        'engine': 'tortoise.backends.asyncpg',
        'credentials': {
            'host': 'localhost',
            'port': '5433',
            'user': 'postgres',
            'password': 'dizainas-77',
            'database': 'fastproject',
        }
    },
    # Using a DB_URL string as in database.py
    #'default': 'postgres://postgres:dizainas-77@db:5432/fastproject'
}, apps={
    'models': {
        'models': ['models', 'aerich.models'],
        # If no default_connection specified, defaults to 'default'
        'default_connection': 'default',
    }
})
