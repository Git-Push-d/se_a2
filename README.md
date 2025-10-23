![Tests](https://github.com/uwidcit/flaskmvc/actions/workflows/dev.yml/badge.svg)

# Flask MVC Template
A template for flask applications structured in the Model View Controller pattern [Demo](https://dcit-flaskmvc.herokuapp.com/). [Postman Collection](https://documenter.getpostman.com/view/583570/2s83zcTnEJ)


# Dependencies
* Python3/pip3
* Packages listed in requirements.txt

# Installing Dependencies
```bash
$ pip install -r requirements.txt
```

# Configuration Management


Configuration information such as the database url/port, credentials, API keys etc are to be supplied to the application. However, it is bad practice to stage production information in publicly visible repositories.
Instead, all config is provided by a config file or via [environment variables](https://linuxize.com/post/how-to-set-and-list-environment-variables-in-linux/).

## In Development

When running the project in a development environment (such as gitpod) the app is configured via default_config.py file in the App folder. By default, the config for development uses a sqlite database.

default_config.py
```python
SQLALCHEMY_DATABASE_URI = "sqlite:///temp-database.db"
SECRET_KEY = "secret key"
JWT_ACCESS_TOKEN_EXPIRES = 7
ENV = "DEVELOPMENT"
```

These values would be imported and added to the app in load_config() function in config.py

config.py
```python
# must be updated to inlude addtional secrets/ api keys & use a gitignored custom-config file instad
def load_config():
    config = {'ENV': os.environ.get('ENV', 'DEVELOPMENT')}
    delta = 7
    if config['ENV'] == "DEVELOPMENT":
        from .default_config import JWT_ACCESS_TOKEN_EXPIRES, SQLALCHEMY_DATABASE_URI, SECRET_KEY
        config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
        config['SECRET_KEY'] = SECRET_KEY
        delta = JWT_ACCESS_TOKEN_EXPIRES
...
```

## In Production

When deploying your application to production/staging you must pass
in configuration information via environment tab of your render project's dashboard.

![perms](./images/fig1.png)

# Flask Commands

wsgi.py is a utility script for performing various tasks related to the project. You can use it to import and test any code in the project. 
You just need create a manager command function, for example:

```python
# inside wsgi.py

user_cli = AppGroup('user', help='User object commands')

@user_cli.cli.command("create-user")
@click.argument("username")
@click.argument("password")
def create_user_command(username, password):
    create_user(username, password)
    print(f'{username} created!')

app.cli.add_command(user_cli) # add the group to the cli

```

Then execute the command invoking with flask cli with command name and the relevant parameters

```bash
$ flask user create bob bobpass
```


# Running the Project

_For development run the serve command (what you execute):_
```bash
$ flask run
```

_For production using gunicorn (what the production server executes):_
```bash
$ gunicorn wsgi:app
```

# Deploying
You can deploy your version of this app to render by clicking on the "Deploy to Render" link above.

# Initializing the Database
When connecting the project to a fresh empty database ensure the appropriate configuration is set then file then run the following command. This must also be executed once when running the app on heroku by opening the heroku console, executing bash and running the command in the dyno.

```bash
$ flask init
```

# Database Migrations
If changes to the models are made, the database must be'migrated' so that it can be synced with the new models.
Then execute following commands using manage.py. More info [here](https://flask-migrate.readthedocs.io/en/latest/)

```bash
$ flask db init
$ flask db migrate
$ flask db upgrade
$ flask db --help
```

# Testing

## Unit & Integration
Unit and Integration tests are created in the App/test. You can then create commands to run them. Look at the unit test command in wsgi.py for example

```python
@test.command("user", help="Run User tests")
@click.argument("type", default="all")
def user_tests_command(type):
    if type == "unit":
        sys.exit(pytest.main(["-k", "UserUnitTests"]))
    elif type == "int":
        sys.exit(pytest.main(["-k", "UserIntegrationTests"]))
    else:
        sys.exit(pytest.main(["-k", "User"]))
```

You can then execute all user tests as follows

```bash
$ flask test user
```

You can also supply "unit" or "int" at the end of the comand to execute only unit or integration tests.

You can run all application tests with the following command

```bash
$ pytest
```

## Test Coverage

You can generate a report on your test coverage via the following command

```bash
$ coverage report
```

You can also generate a detailed html report in a directory named htmlcov with the following comand

```bash
$ coverage html
```

# Troubleshooting

## Views 404ing

If your newly created views are returning 404 ensure that they are added to the list in main.py.

```python
from App.views import (
    user_views,
    index_views
)

# New views must be imported and added to this list
views = [
    user_views,
    index_views
]
```

## Cannot Update Workflow file

If you are running into errors in gitpod when updateding your github actions file, ensure your [github permissions](https://gitpod.io/integrations) in gitpod has workflow enabled ![perms](./images/gitperms.png)

## Database Issues

If you are adding models you may need to migrate the database with the commands given in the previous database migration section. Alternateively you can delete you database file.

# Student incentive system

This is a simple command-line application for managing student community service hours.

## Features
- **Student Login**
  - Request hours confirmation from staff
  - View accolades (10/25/50 hour milestones)
  - View leaderboard

- **Staff Login**
  - Log hours for students
  - Confirm hours requested by students
  - View leaderboard

## Installation & Setup
Clone the repository:

```bash
git clone https://github.com/DominiqueChotack/CommunityTracker_SE-A1-.git
cd CommunityTracker_SE-A1-
```

Install dependencies:
```bash
pip install -r requirements.txt
```

Initialize the database:
```bash
flask init
```

Run the application:
```bash
python3 run.py
# or
flask run
```

The application will be available at `http://localhost:5000`

---

# API Documentation

This application provides a REST API for managing student community service hours. All endpoints require JWT authentication unless otherwise specified.

## Quick Start

### 1. Run the Application
```bash
python3 run.py
```

### 2. Initialize Sample Data
```bash
flask init
```
This creates sample users:
- Students: `alice`, `bob`, `charlie` (password: `password`)
- Staff: `staff1`, `staff2` (password: `password`)

### 3. Test the API
You can use curl, Postman, or any HTTP client to test the endpoints.

---

## Authentication Endpoints

### Login
**POST** `/api/login`

Authenticate a user and receive a JWT token.

**Request Body:**
```json
{
  "username": "alice",
  "password": "password"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response (401 Unauthorized):**
```json
{
  "message": "bad username or password given"
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"password"}'
```

---

### Identify Current User
**GET** `/api/identify`

Get information about the currently authenticated user.

**Headers:**
- `Authorization: Bearer <token>` or Cookie with JWT

**Response (200 OK):**
```json
{
  "message": "username: alice, id : 1"
}
```

**Example:**
```bash
curl -X GET http://localhost:5000/api/identify \
  -H "Cookie: access_token=<your_token>"
```

---

### Logout
**GET** `/api/logout`

Logout the current user (clears JWT cookie).

**Response (200 OK):**
```json
{
  "message": "Logged Out!"
}
```

---

## Student Endpoints

### Get All Students (Staff Only)
**GET** `/api/students`

Retrieve a list of all students.

**Authorization:** Staff only

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "username": "alice",
    "name": "Alice",
    "user_type": "student",
    "total_hours": 15,
    "accolades": [10],
    "confirmation_requested": false
  }
]
```

**Response (403 Forbidden):**
```json
{
  "error": "Unauthorized"
}
```

---

### Get Student by ID
**GET** `/api/students/<student_id>`

Get details of a specific student.

**Authorization:** 
- Students can only view their own profile
- Staff can view any student

**Response (200 OK):**
```json
{
  "id": 1,
  "username": "alice",
  "name": "Alice",
  "user_type": "student",
  "total_hours": 15,
  "accolades": [10],
  "confirmation_requested": false
}
```

**Response (403 Forbidden / 404 Not Found):**
```json
{
  "error": "Unauthorized"
}
```

---

### Get Current Student Profile
**GET** `/api/students/me`

Get the profile of the currently logged-in student.

**Authorization:** Student only

**Response (200 OK):**
```json
{
  "id": 1,
  "username": "alice",
  "name": "Alice",
  "user_type": "student",
  "total_hours": 15,
  "accolades": [10],
  "confirmation_requested": false
}
```

---

### Request Hours Confirmation
**POST** `/api/students/me/request-confirmation`

Student requests confirmation of their hours from staff.

**Authorization:** Student only

**Response (200 OK):**
```json
{
  "message": "Confirmation request sent",
  "student": {
    "id": 1,
    "username": "alice",
    "total_hours": 15,
    "confirmation_requested": true
  }
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/api/students/me/request-confirmation \
  -H "Cookie: access_token=<your_token>"
```

---

### Get Student Accolades
**GET** `/api/students/<student_id>/accolades`

Get accolades (milestone awards) for a student.

**Authorization:**
- Students can only view their own accolades
- Staff can view any student's accolades

**Response (200 OK):**
```json
{
  "accolades": [10, 25, 50]
}
```

**Accolade Milestones:**
- 10 hours
- 25 hours
- 50 hours
- 100 hours

---

### View Leaderboard
**GET** `/api/leaderboard`

Get the leaderboard of all students sorted by total hours (descending).

**Authorization:** Any authenticated user

**Response (200 OK):**
```json
[
  {
    "id": 2,
    "username": "bob",
    "name": "Bob",
    "total_hours": 50,
    "accolades": [10, 25, 50]
  },
  {
    "id": 1,
    "username": "alice",
    "name": "Alice",
    "total_hours": 25,
    "accolades": [10, 25]
  }
]
```

---

## Staff Endpoints

### Get All Staff (Staff Only)
**GET** `/api/staff`

Retrieve a list of all staff members.

**Authorization:** Staff only

**Response (200 OK):**
```json
[
  {
    "id": 3,
    "username": "staff1",
    "name": "Staff One",
    "user_type": "staff"
  }
]
```

---

### Get Current Staff Profile
**GET** `/api/staff/me`

Get the profile of the currently logged-in staff member.

**Authorization:** Staff only

**Response (200 OK):**
```json
{
  "id": 3,
  "username": "staff1",
  "name": "Staff One",
  "user_type": "staff"
}
```

---

### Log Hours for Student
**POST** `/api/staff/log-hours`

Staff logs community service hours for a student.

**Authorization:** Staff only

**Request Body:**
```json
{
  "student_id": 1,
  "hours": 10
}
```

**Response (200 OK):**
```json
{
  "message": "Logged 10 hours for student",
  "student": {
    "id": 1,
    "username": "alice",
    "total_hours": 25,
    "accolades": [10, 25]
  }
}
```

**Response (400 Bad Request):**
```json
{
  "error": "student_id and hours are required"
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/api/staff/log-hours \
  -H "Content-Type: application/json" \
  -H "Cookie: access_token=<staff_token>" \
  -d '{"student_id":1,"hours":10}'
```

---

### Confirm Student Hours
**POST** `/api/staff/confirm-hours`

Staff confirms hours that a student has requested confirmation for.

**Authorization:** Staff only

**Request Body:**
```json
{
  "student_id": 1
}
```

**Response (200 OK):**
```json
{
  "message": "Hours confirmation completed",
  "student": {
    "id": 1,
    "username": "alice",
    "confirmation_requested": false
  }
}
```

**Response (400 Bad Request):**
```json
{
  "error": "No confirmation request from this student"
}
```

---

### Get Pending Confirmations
**GET** `/api/staff/pending-confirmations`

Get all students who have requested hours confirmation.

**Authorization:** Staff only

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "username": "alice",
    "name": "Alice",
    "total_hours": 25,
    "confirmation_requested": true
  }
]
```

---

## Testing the API

### Run All Tests
```bash
pytest
```

### Run Specific Test Files
```bash
# Test authentication API
pytest App/tests/test_auth_api.py -v

# Test student and staff API
pytest App/tests/test_student_staff_api.py -v

# Test general app functionality
pytest App/tests/test_app.py -v
```

### Test Coverage
```bash
# Generate coverage report
coverage run -m pytest
coverage report

# Generate HTML coverage report
coverage html
```

---

## CLI Commands

The application includes helpful CLI commands for managing data:

### Create Students
```bash
flask student create alice password "Alice Student"
flask student list
flask student add-hours 1 10
```

### Create Staff
```bash
flask staff create staff1 password "Staff Member"
flask staff list
flask staff log-hours 3 1 5  # staff_id student_id hours
flask staff pending
```

### View Leaderboard
```bash
flask system leaderboard
```

---

## Error Responses

The API uses standard HTTP status codes:

- **200 OK**: Request succeeded
- **400 Bad Request**: Invalid request data
- **401 Unauthorized**: Missing or invalid JWT token
- **403 Forbidden**: User doesn't have permission
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server error

All error responses include a JSON body with an `error` or `message` field:
```json
{
  "error": "Description of the error"
}
```

---

## Notes for Instructors/Testers

1. **Sample Data**: Run `flask init` to populate the database with test users
2. **Authentication**: All API endpoints (except `/api/login`) require JWT authentication
3. **Authorization**: Students and staff have different permissions - test both user types
4. **Accolades**: Automatically awarded at 10, 25, 50, and 100 hour milestones
5. **Testing**: Comprehensive test suite covers auth, student, and staff APIs (34 tests total)