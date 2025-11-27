# Assignment 2: Database Integration and Transaction Recording

This assignment extends the Kiwi Portfolio Management System with MySQL database integration and transaction recording capabilities.

## New Features

### Database Integration
- **SQLAlchemy ORM**: Full MySQL integration using SQLAlchemy
- **Persistent Storage**: All data (users, portfolios, securities, investments) stored in MySQL
- **Referential Integrity**: Proper foreign key relationships and cascading deletes

### Transaction Recording
- **Automatic Logging**: Every buy and sell operation creates a transaction record
- **Complete History**: Queryable transaction history by user, portfolio, or security
- **Timestamp Tracking**: All transactions timestamped for audit trail

### Data Models
- `User`: User accounts with authentication
- `Portfolio`: Investment portfolios owned by users
- `Security`: Tradable securities (stocks)
- `Investment`: Holdings within portfolios
- `Transaction`: Buy/sell transaction records

## Setup Instructions

### Prerequisites
- Python 3.9+
- MySQL 5.7+ or MariaDB 10.3+

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure MySQL Database

Create a MySQL database:
```sql
CREATE DATABASE kiwi_portfolio CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Set environment variables (or use defaults):
```bash
# Optional - defaults work for standard MySQL setup
export DB_USER=root
export DB_PASSWORD=yourpassword
export DB_HOST=localhost
export DB_PORT=3306
export DB_NAME=kiwi_portfolio
```

### 3. Initialize Database
```bash
python init_db.py
```

This creates all tables and initializes:
- Default admin user (username: admin, password: admin)
- Available securities (AAPL, GOOGL, MSFT, TSLA, etc.)

### 4. Run Application
```bash
# Windows
run_app.bat

# All platforms
python run.py
```

## Running Tests

### Run All Tests
```bash
pytest tests/ -v
```

### Run with Coverage
```bash
pytest tests/ --cov=app --cov-report=html --cov-report=term
```

### View Coverage Report
```bash
# Coverage report saved to htmlcov/index.html
```

## Test Coverage

The test suite includes:
- **Database Operations**: User CRUD, authentication, portfolio management
- **Business Logic**: Buy/sell operations, balance updates, transaction recording
- **Validation**: Input validation, permission checks, error handling
- **Transactions**: Transaction creation, querying, and integrity

Target coverage: **≥80%** across all modules

## Architecture

### Layered Structure
```
app/
├── models.py              # SQLAlchemy data models
├── database.py            # Database configuration
├── db_sqlalchemy.py       # Database operations layer
├── config.py              # Configuration and backend selection
├── service/               # Business logic layer
│   ├── user_service_sqlalchemy.py
│   ├── portfolio_service_sqlalchemy.py
│   └── login_service_sqlalchemy.py
├── domain/                # Domain models
│   ├── User.py
│   ├── Portfolio.py
│   └── Security.py
└── cli/                   # Presentation layer
```

### Database Schema
```
users (id, username, password, first_name, last_name, balance, role)
  └─> portfolios (id, name, description, investment_strategy, user_id)
        └─> investments (id, portfolio_id, security_id, quantity)
              └─> securities (id, ticker, name, reference_price)

transactions (id, user_id, portfolio_id, security_id, type, quantity, price, timestamp)
```

## Key Features Implemented

### 1. Transaction Recording ✓
- Every buy operation creates a BUY transaction
- Every sell operation creates a SELL transaction
- Transactions include: user, portfolio, security, quantity, price, timestamp
- Transactions queryable by user, portfolio, or security

### 2. Database Integration ✓
- MySQL backend with SQLAlchemy ORM
- Proper relationships: User → Portfolio → Investment → Security
- Foreign key constraints with cascading deletes
- Session management for data consistency

### 3. Unit Testing ✓
- pytest-based test suite
- **80%+ code coverage** achieved
- Tests for database operations, business logic, and edge cases
- In-memory SQLite for fast test execution

### 4. Backward Compatibility ✓
- Config-based backend selection
- Can switch between JSON and MySQL backends
- Original functionality preserved

## Default Credentials

**Admin Account:**
- Username: `admin`
- Password: `admin`
- Balance: $10,000
- Role: admin

## Available Securities

- AAPL - Apple Inc. ($175)
- GOOGL - Alphabet Inc. ($140)
- MSFT - Microsoft Corporation ($410)
- TSLA - Tesla Inc. ($250)
- AMZN - Amazon.com Inc. ($145)
- NVDA - NVIDIA Corporation ($450)
- META - Meta Platforms Inc. ($325)
- NFLX - Netflix Inc. ($400)
- SPOT - Spotify Technology S.A. ($180)
- UBER - Uber Technologies Inc. ($65)

## Transaction Query Examples

After running the application and making trades, you can query transactions:

```python
from app import db_sqlalchemy as db

# Get all transactions for a user
transactions = db.query_transactions_by_user("admin")

# Get all transactions for a portfolio
transactions = db.query_transactions_by_portfolio(1)

# Get all transactions for a security
transactions = db.query_transactions_by_security("AAPL")
```

## Code Quality

- **Modular Design**: Clear separation of concerns (models, services, CLI)
- **Error Handling**: Custom exceptions with meaningful error codes
- **Input Validation**: Comprehensive validation at service and database layers
- **Documentation**: Docstrings and comments throughout codebase
- **Type Hints**: Type annotations for better code clarity

## Assignment Requirements Met

✅ MySQL database integration with SQLAlchemy  
✅ Data models for User, Portfolio, Security, Investment, Transaction  
✅ CRUD operations through SQLAlchemy sessions  
✅ Transaction recording for all buy/sell operations  
✅ Transaction history queryable by user/portfolio/security  
✅ pytest-based unit tests with ≥80% coverage  
✅ Fixtures and in-memory database for testing  
✅ Organized tests/ directory structure  
✅ Best practices: separation of concerns, referential integrity  
✅ Clear project structure within app/ directory  

## Notes

- Default MySQL connection uses `root` with no password on `localhost:3306`
- Database name: `kiwi_portfolio`
- Set environment variables to customize database connection
- SQLite used for testing (in-memory, no setup required)
- Original JSON-based backend preserved for reference

## Troubleshooting

### MySQL Connection Error
- Ensure MySQL is running
- Check credentials in environment variables
- Verify database exists: `SHOW DATABASES;`

### Import Error
- Run from project root directory
- Ensure all dependencies installed: `pip install -r requirements.txt`

### Test Failures
- Ensure pytest and pytest-cov installed
- Run tests from project root: `pytest tests/`
