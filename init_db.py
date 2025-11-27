"""
Database initialization script for Kiwi Portfolio Management System.

This script initializes the MySQL database schema and populates it with
default data including an admin user and available securities.
"""

from app.database import init_db, engine
from app import db_sqlalchemy as db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def initialize_database():
    """Initialize database schema and default data"""
    try:
        logger.info("Creating database tables...")
        init_db()
        logger.info("Database tables created successfully")
        
        logger.info("Initializing default admin user...")
        db.initialize_default_admin()
        logger.info("Default admin user created")
        
        logger.info("Initializing securities...")
        securities = {
            "AAPL": ("Apple Inc.", 175.0),
            "GOOGL": ("Alphabet Inc.", 140.0),
            "MSFT": ("Microsoft Corporation", 410.0),
            "TSLA": ("Tesla Inc.", 250.0),
            "AMZN": ("Amazon.com Inc.", 145.0),
            "NVDA": ("NVIDIA Corporation", 450.0),
            "META": ("Meta Platforms Inc.", 325.0),
            "NFLX": ("Netflix Inc.", 400.0),
            "SPOT": ("Spotify Technology S.A.", 180.0),
            "UBER": ("Uber Technologies Inc.", 65.0)
        }
        db.initialize_securities(securities)
        logger.info("Securities initialized")
        
        logger.info("Database initialization complete!")
        return True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        return False


if __name__ == "__main__":
    success = initialize_database()
    if not success:
        exit(1)
