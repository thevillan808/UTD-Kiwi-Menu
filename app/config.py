"""
Bootstrap script to configure database backend.

This allows the application to use either the old JSON-based persistence
or the new MySQL-based persistence by setting USE_SQLALCHEMY.
"""

import os

# Set to True to use MySQL/SQLAlchemy, False to use JSON files
USE_SQLALCHEMY = os.getenv('USE_SQLALCHEMY', 'True').lower() in ('true', '1', 'yes')

if USE_SQLALCHEMY:
    # Use SQLAlchemy backend
    from app import db_sqlalchemy as db
    from app.service import user_service_sqlalchemy as user_service
    from app.service import portfolio_service_sqlalchemy as portfolio_service
    from app.service import login_service_sqlalchemy as login_service
    
    # Initialize database on first import
    try:
        from app.database import init_db
        init_db()
        db.initialize_default_admin()
        
        # Initialize securities
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
    except Exception as e:
        import logging
        logging.warning(f"Database initialization warning: {str(e)}")
else:
    # Use original JSON backend
    from app import db
    from app.service import user_service
    from app.service import portfolio_service
    from app.service import login_service


__all__ = ['db', 'user_service', 'portfolio_service', 'login_service']
