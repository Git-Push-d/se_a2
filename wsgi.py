import click, pytest, sys
from flask.cli import with_appcontext, AppGroup

from App.database import db, get_migrate
from App.models import User, Student, Staff
from App.main import create_app
from App.controllers import (
    create_user,
    get_all_users_json,
    get_all_users,
    initialize,
    create_student,
    create_staff,
    get_all_students_json,
    get_all_staff_json,
    add_hours_to_student,
    get_leaderboard,
    log_hours_for_student,
    confirm_student_hours,
    get_pending_confirmations
)

# This commands file allows you to create convenient CLI commands for testing controllers

app = create_app()
migrate = get_migrate(app)

# This command creates and initializes the database
@app.cli.command("init", help="Creates and initializes the database")
def init():
    initialize()
    print('Database initialized!')

# Student Commands
student_cli = AppGroup('student', help='Student object commands')

@student_cli.command("create", help="Creates a student")
@click.argument("username")
@click.argument("password")
@click.argument("name")
def create_student_command(username, password, name):
    student = create_student(username, password, name)
    print(f'Student {student.name} ({student.username}) created with ID {student.id}!')

@student_cli.command("list", help="Lists all students")
def list_students_command():
    students = get_all_students_json()
    for student in students:
        print(f"ID: {student['id']}, Name: {student['name']}, Hours: {student['total_hours']}, Accolades: {student['accolades']}")

@student_cli.command("add-hours", help="Add hours to a student")
@click.argument("student_id", type=int)
@click.argument("hours", type=int)
def add_hours_command(student_id, hours):
    student = add_hours_to_student(student_id, hours)
    if student:
        print(f'Added {hours} hours to {student.name}. Total: {student.total_hours} hours')
    else:
        print('Student not found')

app.cli.add_command(student_cli)

# Staff Commands
staff_cli = AppGroup('staff', help='Staff object commands')

@staff_cli.command("create", help="Creates a staff member")
@click.argument("username")
@click.argument("password")
@click.argument("name")
def create_staff_command(username, password, name):
    staff = create_staff(username, password, name)
    print(f'Staff {staff.name} ({staff.username}) created with ID {staff.id}!')

@staff_cli.command("list", help="Lists all staff members")
def list_staff_command():
    staff = get_all_staff_json()
    for s in staff:
        print(f"ID: {s['id']}, Name: {s['name']}, Username: {s['username']}")

@staff_cli.command("log-hours", help="Log hours for a student")
@click.argument("staff_id", type=int)
@click.argument("student_id", type=int)
@click.argument("hours", type=int)
def log_hours_command(staff_id, student_id, hours):
    student, error = log_hours_for_student(staff_id, student_id, hours)
    if error:
        print(f'Error: {error}')
    else:
        print(f'Logged {hours} hours for {student.name}. Total: {student.total_hours} hours')

@staff_cli.command("pending", help="Show pending confirmation requests")
def pending_confirmations_command():
    students = get_pending_confirmations()
    if not students:
        print('No pending confirmation requests')
    else:
        for student in students:
            print(f"ID: {student['id']}, Name: {student['name']}, Hours: {student['total_hours']}")

app.cli.add_command(staff_cli)

# System Commands
system_cli = AppGroup('system', help='System commands')

@system_cli.command("leaderboard", help="Display the leaderboard")
def leaderboard_command():
    leaderboard = get_leaderboard()
    print("\n=== Community Service Leaderboard ===")
    for i, student in enumerate(leaderboard, start=1):
        print(f"{i}. {student['name']} - {student['total_hours']} hours (Accolades: {student['accolades']})")
    print()

app.cli.add_command(system_cli)

# User Commands (for general users, kept for compatibility)
user_cli = AppGroup('user', help='User object commands')

@user_cli.command("create", help="Creates a user")
@click.argument("username", default="rob")
@click.argument("password", default="robpass")
def create_user_command(username, password):
    create_user(username, password, "Generic User")
    print(f'{username} created!')

@user_cli.command("list", help="Lists users in the database")
@click.argument("format", default="string")
def list_user_command(format):
    if format == 'string':
        print(get_all_users())
    else:
        print(get_all_users_json())

app.cli.add_command(user_cli)

# Test Commands
test = AppGroup('test', help='Testing commands')

@test.command("user", help="Run User tests")
@click.argument("type", default="all")
def user_tests_command(type):
    if type == "unit":
        sys.exit(pytest.main(["-k", "UserUnitTests"]))
    elif type == "int":
        sys.exit(pytest.main(["-k", "UserIntegrationTests"]))
    else:
        sys.exit(pytest.main(["-k", "User"]))

@test.command("student", help="Run Student tests")
@click.argument("type", default="all")
def student_tests_command(type):
    if type == "unit":
        sys.exit(pytest.main(["-k", "StudentUnitTests"]))
    elif type == "int":
        sys.exit(pytest.main(["-k", "StudentIntegrationTests"]))
    else:
        sys.exit(pytest.main(["-k", "Student"]))

@test.command("staff", help="Run Staff tests")
@click.argument("type", default="all")
def staff_tests_command(type):
    if type == "unit":
        sys.exit(pytest.main(["-k", "StaffUnitTests"]))
    elif type == "int":
        sys.exit(pytest.main(["-k", "StaffIntegrationTests"]))
    else:
        sys.exit(pytest.main(["-k", "Staff"]))

@test.command("all", help="Run all tests")
def all_tests_command():
    sys.exit(pytest.main(["-v"]))

app.cli.add_command(test)
