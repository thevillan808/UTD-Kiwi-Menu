from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from urllib.parse import quote_plus
from .models import Base

# Load environment variables from .env file
load_dotenv()

# Get database credentials from environment variables
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '3306')
DB_NAME = os.getenv('DB_NAME', 'kiwi_portfolio')

# URL encode the password to handle special characters
encoded_password = quote_plus(DB_PASSWORD) if DB_PASSWORD else ''

# Create connection string for MySQL
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create database engine
engine = create_engine(DATABASE_URL, echo=False)

# Create session factory
SessionLocal = sessionmaker(bind=engine)

def init_db():
    # Create all tables
    Base.metadata.create_all(bind=engine)

def get_session():
    # Get new database session
    return SessionLocal()

def close_session(session):
    # Close database session
    if session:
        session.close()
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from urllib.parse import quote_plus
from .models import Base

# Load environment variables from .env file
load_dotenv()

# Get database credentials from environment variables
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '3306')
DB_NAME = os.getenv('DB_NAME', 'kiwi_portfolio')

# URL encode the password to handle special characters
encoded_password = quote_plus(DB_PASSWORD) if DB_PASSWORD else ''

# Create connection string for MySQL
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create database engine
engine = create_engine(DATABASE_URL, echo=False)

# Create session factory
SessionLocal = sessionmaker(bind=engine)

def init_db():
    # Create all tables
    Base.metadata.create_all(bind=engine)

def get_session():
    # Get new database session
    return SessionLocal()

def close_session(session):
    # Close database session
    if session:
        session.close()
