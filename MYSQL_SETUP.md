# MySQL Setup for Kiwi Portfolio API

## Quick Fix Options

### Option 1: Set Environment Variable (Recommended)
```cmd
set DB_PASSWORD=your_actual_password
python run.py
```

### Option 2: Create .env file
1. Copy `.env.template` to `.env`
2. Update `DB_PASSWORD=your_actual_password`
3. Install python-dotenv: `pip install python-dotenv`
4. Run: `python run.py`

### Option 3: Direct Database Setup
If MySQL is not set up, create the database:

```sql
CREATE DATABASE kiwi_portfolio;
CREATE USER 'root'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON kiwi_portfolio.* TO 'root'@'localhost';
FLUSH PRIVILEGES;
```

### Option 4: Test Different Passwords
Common MySQL default passwords:
- `password` (most common for dev)
- `` (empty string)
- `root`
- `mysql`

## Current Configuration
The app now uses environment variables with fallback to `password`:
- DB_USER: root
- DB_PASSWORD: password (default, change via environment)
- DB_HOST: localhost
- DB_PORT: 3306
- DB_NAME: kiwi_portfolio

## Verify MySQL is Running
```cmd
mysql -u root -p
```

If MySQL is not installed or not running, install/start it first.
