# Assignment 3: Transitioning Your Local Application to a Web Service

Please read the following instructions carefully to ensure proper submission and compliance with the application requirements.

## Purpose of This Assignment

In Assignment 2, you transformed your command-line (CLI) investment management application into a database-backed program using MySQL, SQLAlchemy models, and automated tests. You replaced mock persistence with real database operations and established systematic test coverage. At this stage, you have a functional and testable local application.

Assignment 3 expands your project into a web service. Your goal is to expose your application’s data and functionality over the web using Flask, a lightweight Python framework for building web applications and APIs. You will refactor your existing architecture so that users (or client applications such as Postman or JavaScript front-ends) can interact with your program via HTTP requests instead of the command line.
General steps for approaching the assignment:

1. Uplift local application to a web service app.
2. Refactor database setup so that database operations operate in a web based architecture.
3. Refactor existing logic modules/functions (where needed) to make them useable for a web application.
4. Expose functions using mapped routes.
5. Test (manually) that your routes work as expected.

## Learning Objectives

After completing this assignment, you should be able to:

- Convert a local CLI-based application into a network-accessible web service.
- Structure a Flask application using the application factory pattern.
- Configure a Flask app using a configuration object.
- Integrate SQLAlchemy with Flask using flask_sqlalchemy.
- Refactor business logic for a web-based architecture.
- Expose functions through HTTP routes.
- Manually test your API using an HTTP client.

## Assignment Requirements (High-Level Overview)

To complete this assignment successfully, you will:

1. Uplift your existing local application into a Flask web application.
2. Refactor your database setup to use flask_sqlalchemy.
3. Refactor your service-layer logic to remove assumptions of console input or an active logged-in user.
4. Expose functionality as HTTP routes organized using Flask blueprints (see [minimum requirements](#minimum-requirements)).
5. Manually test your routes using Postman or another API-testing tool.

Each section below explains these steps in detail.

## Environment and Dependencies

You must install additional dependencies to support Flask and SQLAlchemy integration in a web application.

`pip install flask flask_sqlalchemy`

After installing these packages, update requirements.txt:

`pip freeze > requirements.txt`

This ensures your virtual environment is reproducible and consistent across environments.

## 1. From Local to Web Application

What you've developed so far is a local application that is trigged by executing a python module (`main.py`). This main module starts a command line based interface that takes requests from users, execute appropriate functions, then print response back to the console.

Making this a web based application means that when you execute the main module you won't get a command line interface but instead you would start a web server that listens on a specific port for HTTP requests (similar to the ones that users were providing on the command line), maps requests to functions (using [routes and blueprints](https://github.com/mab105120/ftec-notes/blob/main/classroom_handouts/web-services-1.md#routes-and-blueprints)), execute functions, then return the response.

> ⚠️ IMPORTANT ⚠️  
>
> There are, at least two, major differences between the command-line application and the web service that both need to be addressed:
>
>1. The CLI application takes in user actions as input from the command line. This is not possible with web services. Instead user input is included in the HTTP request (Remember there are three ways to send data in the HTTP request: 1) using [query path](https://github.com/mab105120/ftec-notes/blob/main/classroom_handouts/web-services-1.md#query-parameters), 2) using [path parameters](https://github.com/mab105120/ftec-notes/blob/main/classroom_handouts/web-services-1.md#path-parameters), 3) using [JSON](https://github.com/mab105120/ftec-notes/blob/main/classroom_handouts/web-services-1.md#json-as-a-data-format-for-web-services) in the [request body](https://github.com/mab105120/ftec-notes/blob/main/classroom_handouts/web-services-1.md#sending-json-data-in-the-request-body))
>2. The CLI application implemented a login service that accepts username/password from the user and matches it with data from the database. Authentication with web services is drastically different. We have not yet covered this topic so for the purpose of this assignment you are __not__ required to handle user authentication. Note that some functions (e.g., `create_portfolio()`) need to know the logged in user to assign the new portflio to them. Since we are not implementing an authentication service as part of this assignment, the client will need to pass in the user in the HTTP request.
>
> See this [section](#refactor-existing-logic-modules) for more details on how to address these issues.

### Guide

Follow these steps to uplift your application to a web app:

- If it doesn't exist already create a `__init__.py` file in your `app` package. This file will contain the code that creates the web application.
- Use the [factory pattern](https://github.com/mab105120/ftec-notes/blob/main/classroom_handouts/web-services-1.md#building-the-application-using-the-factory-pattern) to define a function that creates a flask application.
- This function must also configure the flask application before returning it. To learn more about flask application configuration see [this](https://github.com/mab105120/ftec-notes/blob/main/classroom_handouts/web-services-1.md#application-configuration). The main thing to understand is when you create a flask application you can pass a configuration object that configures the application behavior (e.g., `app.config.from_object(config_class)`). The configuration object is simply a python class where some options are defined to guide the application behavior (e.g., the `SQLALCHEMY_DATABASE_URI` variable in the config [class](https://github.com/mab105120/ftec-notes/blob/main/classroom_handouts/web-services-1.md#application-configuration) simply tells the flask application what connection string to use when using SQL Alchemy to connect to a database).
- Once the application is created and configured (later you will also need to register extensions and blueprints here) the function should return the application object.
- Now that you have a function to create a flask app you need to modify your `main.py` module so that when it is executed it starts the flask application instead of starting the command line interface.

```python
# app/main.py
from app import create_app # import the create_app function that creates a flask application from the app pacakge.
from app.config import Config
app=create_app(Config)
if __name__=="__main__": # this checks whether this module is executed directly.
    app.run()
```

Now when you start the application `>python3 -m app.main` it should start a local web server. You should see something like this printed to the console:

```bash
* Serving Flask app 'app'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 734-280-764
 ```

Of course so far there isn't much that is interesting about the server (until you register [extensions](#25-register-db-object-as-flask-extension) and [blueprints](#register-blueprints)) but you at least have the foundation ready.

## 2. Refactor Database Setup

Your application currently initializes SQLAlchemy manually by creating an engine and session factory. When building a web service, Flask offers a more tightly integrated approach through the [`flask_sqlalchemy`](https://flask-sqlalchemy.readthedocs.io/en/stable/) extension.

You must update your database configuration to use Flask’s integration following these steps:

1. Create a new `db` instance using the `flask_sqlalchemy` library.
2. Change the base class that your model classes extend to use `db.Model` from the object that you created in step 1.
3. Change your service modules to create a session using the new `db` object instead of the `get_session()` function that you are currently using.
4. Add a connection string to the configuration object.
5. Register the new `db` object as flask extension

### 2.1 Create new db object

Under the app package create a new module called `db.py` (PS: if you already have a module with this name then call the new module `database.py`). In this module you will need to create a `db` object as such:

```python
# app/db.py
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
```

As easy as that!

### 2.2 Uplift model classes to use new `db` object

In each of your model class modules (e.g., User, Portfolio, Security, etc.) change the super class that your class extends to `db.Model` instead of `Base`:

Before the change your code (roughly) looked something like this:

```python
# app/domain/user.py
from app.database import Base

class User(Base):
    __tablename__ = 'user'
    username: Mapped[str] = mapped_column(String(30), primary_key=True)
    #...
```

After the change your code should (roughly) look something like this:

```python
# app/domain/user.py
from app.db import db # from the new db module import the db object

class User(db.Model):
    __tablename__ = 'user'
    username: Mapped[str] = mapped_column(String(30), primary_key=True)
    #...
```

### 2.3 Uplift service modules to use session from new `db` object

With `flask_sqlalchemy` getting a database session is a lot easier than what we had to do for the local app:

With the local app we needed to create an `engine` object and then a `get_session()` helper function that created a session from the engine. Example:

```python
# app/database.py
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session

engine = create_engine(url=create_connection_string()) # 1. create an engine object.

LocalSession = sessionmaker( # 2. create a session maker bound to the engine.
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False
 )

def get_session() -> Session: # 3. create a helper function to return a new session object.
    return LocalSession()
```

Then in the service modules when we needed to get the session we simply:

```python
# app/services/user_service.py
from app.database import get_session()

def get_user_by_id(int: id) -> User:
    session = get_session()
    return session.query(User).filter_by(id=id).one()
```

With the `flask_sqlalchemy` library we don't have to create an engine and a helper session creating function. Instead when we want a session to the database we simply use `db.session` from the `db` object:

```python
# app/services/user_service.py
from app.db import db

def get_user_by_id(int: id) -> User:
    session = db.session
    return session.query(User).filter_by(id=id).one()
```

So you need to replace all instances of `get_session()` to `db.session`.

### 2.4 Configuration

Now that we're using `flask_sqlalchemy` the way that we provide the connection string to the database changes. The `flask_sqlalchemy` library makes passing the connection string easy! All that you have to do is to create a variale called `SQLALCHEMY_DATABASE_URI` in the `Config` class and set the value to the connection string:

```python
# app/config.py
database_config = {
    'host': 'localhost',
    'port': 3306,
    'user': 'user',
    'password': 'password',
    'database': 'database'
}

class Config:
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{database_config.get('user')}:{database_config.get('password')}@{database_config.get('host')}:{database_config.get('port')}/{database_config.get('database')}"
```

### 2.5 Register `db` object as flask extension

Remember so far the flask application that is being returned from the `create_app()` function in the `__init__.py` file of the `app` package only creates the flask application and configures it but it __does not__ register any extensions. Now that we have the `db` object from the flask_sqlalchemy library, we need to register it with the flask app in the `create_app()` function:

```python
# app/__init__.py
from flask import Flask
from app.db import db

def create_app(config): 
    app = Flask(__name__)
    app.config.from_object(config)
    # register extensions
    db.init_app(app)
    
    return app
```

## Refactor existing logic modules

Since we're now changing the application from a command line interface to a web interface we need to refactor some of the business logic functions in the services modules.

For example:

- Your service module functions might be collecting user input from the console. With a web based application the user does not have access to the console so this pattern does not work.
- Some functions needed to know the current logged in user which, with what we've covered so far, is not possible for a web app.

We'll need to refactor the code to make sure that the logic functions in the service module work for a web service based architecture.

> __Note on login functionality in web services__  
So far your local application handled authentication directly by asking the user for a username/password from the console and then comparing the values to what exists in the database. Once a user is logged in, the user is remembered in the session so that it is used in some functions (e.g., creating a portfolio requires knowing who the logged in user is to associate the portfolio with).  
Authentication with web services is drastically different than this. We will cover authentication in more detail next semester. For the time being, for this assignment, there will be __no login feature__ and anywhere a function requires knowing the logged_user, that data should be passed directly through the request.

As an example, consider the following implementation of the `create_portfolio()` function:

```python
# app/services/portfolio_service.py
def create_portfolio() -> str:
    user_inputs = collect_inputs({
        "Portfolio name": "name",
        "Portfolio description": "description" 
    })
    name = user_inputs["name"]
    description = user_inputs["description"]
    user = get_logged_in_user()
    # ...
```

notice here that there are two issues:

1. The function requests console input from the user, which will not be possible in a web service.
2. The function gets the logged in user using `get_logged_in_user()` function. But since we have not yet implemented authentication with web services there is no function like this to use. Instead we need to pass the portfolio user/owner as a request parameter.

To address both of these issues the code must be refactored so that any data expected from the user console input + logged in user should be passed as parameters to the function. Example:

```python
# app/services/portfolio_service.py
def create_portfolio(name: str, description: str, user: str) -> str:
    portfolio = Portfolio(name=name, description=description, owner=user.username)
    try:
        session = db.session
        session.add(portfolio)
        session.commit()
    # ...
```

with this change the function no longer depends on user input from the console or getting the user from `get_logged_in_user()` (PS: this data will be supplied by the user later in the HTTP request).

## Expose Functions

The main objective of a web service is to expose python functions over a network. The command line application offers a lot of functionality. We can group those functionality by their business purpose into user, portfolio, security functions. Each of those are a group of functions that act on a similar object (e.g., functions in the user service module create/delete/update/etc users).

Now we want to map those functions to routes. The best practice is to create a separate package in the project root called `routes`. This package will contain the modules that have the code to map functions to routes. In order to continue with the same organization structure, we will create a separate module for user routes, portfolio routes, and security routes.

```python
# app/route/portfolio_bp.py
from flask import Blueprint, request
from app.service.portfolio_service import create_portfolio

portflio_bp = Blueprint('portfolio', __name__)

@portflio_bp.route('/create', methods = ['POST'])
def create_portfolio():
    data = request.get_json()
    try:
        data = request.get_json() # we will send data using JSON in the body of the request
        name = data.get('name')
        description = data.get('description')
        owner = data.get('owner')
        message = create_portfolio(name, description, owner)
        return {"message": message}, 201
    except Exception as e:
        return {"error": str(e)}, 400

```

Note: in the implementation above we assume that the caller is sending the data in the body of the request object in JSON format. To learn more about this pattern see [this](https://github.com/mab105120/ftec-notes/blob/main/classroom_handouts/web-services-1.md#json-as-a-data-format-for-web-services). When data is passed in the request or response body, often times we need to convert data between python format and JSON. To learn more see [this](https://github.com/mab105120/ftec-notes/blob/main/classroom_handouts/web-services-1.md#how-data-is-converted-between-python-and-json).

### Register Blueprints

Now that we creates modules that contain blueprints which define the mapping between routes and functions we need to register the blueprints when creating the flask application. Example:

```python
# app/__init__.py
from flask import Flask
from app.db import db
from app.route.user_bp import user_bp

def create_app(config): 
    app = Flask(__name__)
    app.config.from_object(config)
    # register extensions
    db.init_app(app)
    # register blueprints
    app.register_blueprint(user_bp)
    return app
```

Now after your blueprints have been registered when you start the web application by executing the `main` module, you computer will start listening on the specific port (Flask defaults to port 5000). Any requests that come in that match the pattern defined in the blueprint routes will execute the function that the route is mapped to.

## Testing your application

Automated testing is out of scope for this assignment. To test that your application works as expected you need to:

1. Start your application locally by executing the `main` module.
2. Use an HTTP client such as [postman](https://www.postman.com/downloads/) to send HTTP requests and confirm that the application works as expected. Note: you can download postman for free without needing to sign up.

## Minimum Requirements

At a minimum your assignment submission must create routes to expose the following functionality:

__User Blueprint__:

1. getting all users
2. getting a user by id
3. create a new user
4. delete an existing user

__Portfolio Blueprint__:

1. getting all portfolios
2. getting a portfolio by id
3. creating a portfolio
4. deleting a portfolio
5. adding a new security to an existing portfolio.
6. harvesting an investment from an existing portfolio.

__Security Blueprint__:

1. getting all available securities.

## Technical Guidelines

- Update your existing `requirements.txt` to include any new dependencies.
- Ensure your code runs without modification on another machine with equivalent setup (MySQL + Python environment).
- Maintain a clear and modular project structure within the existing app/ directory.
- Follow good design principles:
  - Separate data models, services, and routes.
  - Keep database logic and business logic decoupled.

## Submission Instructions

- Submit your work by creating a pull request (PR) from your feature branch (e.g., assignment-3) into your main branch on GitHub.

⚠️ __DO NOT__ merge the request to main. All code must be reviewed before it can be merged to main.

Late submissions are subject to standard course penalties unless prior approval is obtained.

## Evaluation Criteria

| Criterion | Weight |
| :---------| :-------|
|Functionality & Feature Completion | 40%|
|Sound web service implementation | 25%|
|Code Quality & Organization | 10%|
|Exception Handling & Stability | 15%|
|Version Control & Submission Compliance | 10%|
