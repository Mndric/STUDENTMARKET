# config.py
import os
from dotenv import load_dotenv
load_dotenv()

# Ensure the MongoDB URI includes a database name because Flask-PyMongo
# (v2+) only sets `mongo.db` when the URI contains the database.
try:
    from pymongo import uri_parser
except Exception:
    uri_parser = None


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    # env names: MONGODB_URI (full URI) and MONGODB_DB (database name)
    _mongo_uri_env = os.environ.get('MONGODB_URI')
    _mongo_db_env = os.environ.get('MONGODB_DB', 'pzw')

    if _mongo_uri_env:
        # If the provided URI doesn't include a database, append the DB name.
        database_name = None
        if uri_parser is not None:
            try:
                parsed = uri_parser.parse_uri(_mongo_uri_env)
                database_name = parsed.get('database')
            except Exception:
                database_name = None
        if database_name:
            MONGO_URI = _mongo_uri_env
        else:
            MONGO_URI = _mongo_uri_env.rstrip('/') + '/' + _mongo_db_env
    else:
        MONGO_URI = f'mongodb://localhost:27017/{_mongo_db_env}'

    MONGO_DBNAME = _mongo_db_env
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 465))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'False') == 'True'
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'True') == 'True'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@studentmarket.local')
    MAIL_TIMEOUT = int(os.environ.get('MAIL_TIMEOUT', 10))
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    REMEMBER_COOKIE_DURATION = 7  # days
    ITEMS_PER_PAGE = 10
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD_HASH = os.environ.get('ADMIN_PASSWORD_HASH')
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@studentmarket.local')

class DevelopmentConfig(Config):
    DEBUG = True
    SESSION_COOKIE_SECURE = False

class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
