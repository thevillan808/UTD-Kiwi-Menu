# Assignment 2: Database Integration, Transactions, and Unit Testing

Course: Financial Applications of Web Development
Due Date: November 19, 2025 – 11:59 PM CST
Submission Method: Merge Request on the student’s GitHub repository

## Overview

In Assignment 1, you built a command-line portfolio management application that allowed users to:

- Add and view users
- Create portfolios for each user
- Add investments to portfolios
- Liquidate (sell) existing investments

For that assignment, the database layer was mocked — data existed only in memory and was lost each time the program exited.

In Assignment 2, you will extend and refactor your application to persist data using a MySQL database and add a transaction recording feature. You will also implement automated unit tests to ensure code reliability and maintainability.

## Objectives

By completing this assignment, you will:

1. Integrate a local MySQL database with SQLAlchemy.
2. Create data models for users, portfolios, investments, securities, and transactions.
3. Replace mocked persistence logic with real database operations.
4. Implement a transaction-logging feature that records every buy and sell order.
5. Develop pytest-based unit tests achieving at least 80% coverage across database and business logic layers.

## Functional Requirements

### Transaction Recording Feature

- Each buy or sell operation must generate a transaction record.

- Each record should include, at minimum:

  - Transaction ID (auto-generated)
  - User ID
  - Portfolio ID
  - Security ID (representing the traded asset)
  - Transaction type (“BUY” or “SELL”)
  - Quantity and price
  - Timestamp

- The transaction history must be queryable for any user, portfolio, or security.

### Database Integration

Use MySQL as the backend database.

Define SQLAlchemy models for:

- `User`
- `Portfolio`
- `Security`
- `Investment`
- `Transaction`

Refactor existing services so CRUD operations are executed through SQLAlchemy sessions rather than mocked data structures.

Apply best practices for:

- Session creation and teardown
- Use of declarative base
- Foreign-key relationships between entities (e.g., one-to-many between User → Portfolio, one-to-many between Portfolio → Investment, etc.)
- Referential integrity (e.g., transactions referencing a valid security and portfolio)

### Unit Testing

- Use pytest as the testing framework.
- Achieve at least 80% test coverage across:
  - Business logic (e.g., order placement, liquidation, transaction logging)
  - Database operations (insert, update, delete, query)
- Use fixtures and in-memory databases (e.g., SQLite) or temporary test schemas to isolate test cases.
- Organize tests in a dedicated `tests/` directory.

## Technical Guidelines

- Update your existing requirements.txt to include any new dependencies (e.g., sqlalchemy, pytest, pytest-cov, pymysql).
- Ensure your code runs without modification on another machine with equivalent setup (MySQL + Python environment).
- Maintain a clear and modular project structure within the existing app/ directory.
- Follow good design principles:
  - Separate data models, services, and CLI entry points.
  - Keep database logic and business logic decoupled.
  - Ensure that the Security model encapsulates details about available assets (e.g., symbol, name, type, price).

## Submission Instructions

- Submit your work by creating a merge request (MR) from your feature branch (e.g., assignment-2) into your main branch on GitHub.
- The MR description should include:
  - A summary of implemented features
  - Instructions for setting up and running tests
  - A statement of achieved test coverage (e.g., pytest coverage report snippet)

Late submissions are subject to standard course penalties unless prior approval is obtained.

## Evaluation Criteria

|Criterion|Weight|Description
|--|--|--|
|Automated Testing (pytest, ≥ 80% coverage)|40%|Test completeness, coverage, and clarity
|Transaction Feature Implementation|25%|Correctness and accuracy of transaction recording
|Database Integration (SQLAlchemy + MySQL)|25%|Proper modeling, relationships, and CRUD operations
|Code Quality and Structure|10%|Readability, modularity, adherence to best practices.
