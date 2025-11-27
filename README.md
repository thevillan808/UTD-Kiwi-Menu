# UTD Kiwi CLI

A command-line portfolio management application built for UTD coursework.

## Features

- User authentication and role management (admin/user)
- Portfolio creation and management
- Stock trading simulation (buy/sell operations)
- Market data integration
- Admin-only user management with clear UI indicators
- Comprehensive input validation and security

## Quick Start

### Running the Application
```bash
# Windows
run_app.bat

# All platforms  
python -m app.main
# OR
python run.py
```

### Running Tests
```bash
# Windows (recommended)
run_tests.bat

# All platforms
python tools/test_comprehensive.py
```

## Project Structure

```
app/                    # Main application code
├── cli/               # Command-line interface
├── domain/            # Business logic and models  
├── service/           # Service layer
└── db.py              # Data persistence

tools/                 # Testing and utilities
├── test_comprehensive.py    # Main test suite (50+ tests)
├── run_tests.bat           # Windows test runner
└── TEST_COVERAGE.md        # Test documentation

run_app.bat            # Windows app launcher
run_tests.bat          # Windows test runner
requirements.txt       # Python dependencies
```

## Requirements

- Python 3.9+
- Rich library (for colored console output)
- bcrypt (for password hashing)

## Installation

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the application: `run_app.bat` (Windows) or `python run.py`

## Testing

The project includes a comprehensive test suite with 50+ tests covering:
- Authentication and session management
- User management and admin protection
- Portfolio operations and validation
- Edge cases and security testing
- Menu validation and input handling

Run tests with: `run_tests.bat` (Windows) or `python tools/test_comprehensive.py`

## Development

- **Language**: Python 3.9+
- **Architecture**: Layered (CLI → Service → Domain → DB)
- **Testing**: Comprehensive suite with ASCII-compatible output
- **Persistence**: JSON file storage with bcrypt password hashing
- **UI**: Rich console interface with colored output
