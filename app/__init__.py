import logging
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(dotenv_path=env_path)
except ImportError:
    pass
except Exception as e:
    logging.debug(f'Could not load .env: {e}')

logging.basicConfig(
    filename='kiwi_api_debug.log',
    filemode='w',
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(message)s'
)

from flask import Flask
from .db import db

class Config:
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '3306')
    DB_NAME = os.getenv('DB_NAME', 'kiwi_portfolio')
    
    from urllib.parse import quote_plus
    _encoded_password = quote_plus(DB_PASSWORD)
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{DB_USER}:{_encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)
    from . import models
    
    from .routes import api
    app.register_blueprint(api, url_prefix="/api")
    
    return app
