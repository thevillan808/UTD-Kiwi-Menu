"""
Initialize database for Flask application using flask_sqlalchemy
Creates all tables defined in models.py
"""
from app import create_app
from app.db import db
def init_database():
    """Create all database tables"""
    print("Initializing database...")
    # Create Flask application
    app = create_app()
    # Create all tables within application context
    with app.app_context():
        print("Creating all tables...")
        db.create_all()
        print("✅ Database tables created successfully!")
        # Print created tables
        print("\nCreated tables:")
        for table in db.metadata.tables.keys():
            print(f"  - {table}")
if __name__ == '__main__':
    init_database()
