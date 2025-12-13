# Kiwi Portfolio Manager

Portfolio management web application for FTEC 6V97.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Setup MySQL database:
```bash
python init_db.py
```

3. Run the application:
```bash
python run.py
```

The API will be available at `http://127.0.0.1:5000/api`

## API Endpoints

### Users
- GET `/api/users` - Get all users
- POST `/api/users` - Create user
- GET `/api/users/<username>` - Get user
- DELETE `/api/users/<username>` - Delete user

### Portfolios
- GET `/api/portfolios` - Get all portfolios
- POST `/api/portfolios` - Create portfolio
- GET `/api/portfolios/<id>` - Get portfolio
- DELETE `/api/portfolios/<id>` - Delete portfolio

### Investments
- POST `/api/portfolios/<id>/securities` - Add security
- DELETE `/api/portfolios/<id>/securities/<ticker>` - Remove security

### Securities
- GET `/api/securities` - Get all securities
- POST `/api/securities` - Create security

## Testing

Run tests:
```bash
pytest tests/
```

Run with coverage:
```bash
pytest tests/ --cov=app
```

## Requirements

- Python 3.9+
- Flask
- Flask-SQLAlchemy
- MySQL
- PyMySQL
