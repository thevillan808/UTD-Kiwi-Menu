# Kiwi Menu Flask API Documentation

## Base URL
`/api`

## Endpoints

### Users
- `GET /api/users` — List all users
- `POST /api/users` — Create a new user
  - JSON body: `{ "username": str, "password": str, "first_name": str, "last_name": str, "balance": float, "role": str }`

### Portfolios
- `GET /api/portfolios` — List all portfolios
- `POST /api/portfolios` — Create a new portfolio
  - JSON body: `{ "name": str, "description": str, "investment_strategy": str, "username": str }`

### Securities
- `GET /api/securities` — List all securities
- `POST /api/securities` — Create a new security
  - JSON body: `{ "ticker": str, "name": str, "reference_price": float }`

### Transactions
- `GET /api/transactions/security/<ticker>` — List all transactions for a security

## Example Usage
- To create a user:
  ```bash
  curl -X POST http://127.0.0.1:5000/api/users -H "Content-Type: application/json" -d '{"username":"alice","password":"pw","first_name":"Alice","last_name":"Smith","balance":1000,"role":"user"}'
  ```

- To list all users:
  ```bash
  curl http://127.0.0.1:5000/api/users
  ```

- To create a portfolio:
  ```bash
  curl -X POST http://127.0.0.1:5000/api/portfolios -H "Content-Type: application/json" -d '{"name":"Growth","description":"Aggressive growth","investment_strategy":"Growth","username":"alice"}'
  ```

- To list all portfolios:
  ```bash
  curl http://127.0.0.1:5000/api/portfolios
  ```
