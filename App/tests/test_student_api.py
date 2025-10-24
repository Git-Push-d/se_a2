import os, tempfile, pytest, logging, unittest
import json
from werkzeug.security import check_password_hash, generate_password_hash

from App.main import create_app
from App.database import db, create_db
from App.models import User, Student, Staff
from App.controllers import (
    create_student,
    create_staff,
    add_hours_to_student,
    login
)


LOGGER = logging.getLogger(__name__)


def get_auth_headers(client, username, password):
    """Helper function to login and get Authorization header"""
    response = client.post('/api/login',
        data=json.dumps({'username': username, 'password': password}),
        content_type='application/json'
    )
    if response.status_code == 200:
        token = response.json['access_token']
        return {'Authorization': f'Bearer {token}'}
    return {}


'''
   Unit Tests
'''
class StudentUnitTests(unittest.TestCase):

    def test_student_creation(self):
        """Test student model creation"""
        student = Student("teststudent", "password", "Test Student")
        assert student.username == "teststudent"
        assert student.name == "Test Student"
        assert student.total_hours == 0
        assert student.confirmation_requested == False

    def test_student_add_hours(self):
        """Test adding hours to student"""
        student = Student("student1", "pass", "Student One")
        student.add_hours(5)
        assert student.total_hours == 5
        student.add_hours(3)
        assert student.total_hours == 8

    def test_student_request_confirmation(self):
        """Test student requesting confirmation"""
        student = Student("student1", "pass", "Student One")
        assert student.confirmation_requested == False
        student.request_confirmation()
        assert student.confirmation_requested == True


'''
    Integration Tests
'''

@pytest.fixture(autouse=True, scope="module")
def empty_db():
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
    create_db()
    yield app.test_client()
    db.drop_all()


class StudentAPIIntegrationTests(unittest.TestCase):

    def test_get_students_as_staff(self):
        """Test getting all students as staff member"""
        staff = create_staff("stafftest1", "password", "Staff Test")
        student = create_student("studenttest1", "password", "Student Test")

        app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
        client = app.test_client()

        headers = get_auth_headers(client, 'stafftest1', 'password')

        response = client.get('/api/students', headers=headers)

        assert response.status_code == 200
        students = response.json
        assert isinstance(students, list)
        assert len(students) > 0

    def test_get_students_as_student_forbidden(self):
        """Test that students cannot view all students list"""
        student = create_student("studenttest2", "password", "Student Test 2")

        app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
        client = app.test_client()

        headers = get_auth_headers(client, 'studenttest2', 'password')

        response = client.get('/api/students', headers=headers)

        assert response.status_code == 403

    def test_get_student_by_id(self):
        """Test getting a specific student by ID"""
        student = create_student("studenttest3", "password", "Student Test 3")

        app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
        client = app.test_client()

        headers = get_auth_headers(client, 'studenttest3', 'password')

        response = client.get(f'/api/students/{student.id}', headers=headers)

        assert response.status_code == 200
        data = response.json
        assert data['username'] == 'studenttest3'
        assert data['name'] == 'Student Test 3'

    def test_get_student_unauthorized(self):
        """Test that a student cannot view another student's details"""
        student1 = create_student("studenttest4", "password", "Student Test 4")
        student2 = create_student("studenttest5", "password", "Student Test 5")

        app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
        client = app.test_client()

        headers = get_auth_headers(client, 'studenttest4', 'password')

        response = client.get(f'/api/students/{student2.id}', headers=headers)

        assert response.status_code == 403

    def test_get_current_student(self):
        """Test getting current student's profile"""
        student = create_student("studenttest6", "password", "Student Test 6")

        app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
        client = app.test_client()

        headers = get_auth_headers(client, 'studenttest6', 'password')

        response = client.get('/api/students/me', headers=headers)

        assert response.status_code == 200
        data = response.json
        assert data['username'] == 'studenttest6'

    def test_request_hours_confirmation(self):
        """Test student requesting hours confirmation"""
        student = create_student("studenttest7", "password", "Student Test 7")

        app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
        client = app.test_client()

        headers = get_auth_headers(client, 'studenttest7', 'password')

        response = client.post('/api/students/me/request-confirmation', headers=headers)

        assert response.status_code == 200
        data = response.json
        assert 'message' in data
        assert data['student']['confirmation_requested'] == True

    def test_get_student_accolades(self):
        """Test getting student accolades"""
        student = create_student("studenttest8", "password", "Student Test 8")
        add_hours_to_student(student.id, 15)

        app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
        client = app.test_client()

        headers = get_auth_headers(client, 'studenttest8', 'password')

        response = client.get(f'/api/students/{student.id}/accolades', headers=headers)

        assert response.status_code == 200
        data = response.json
        assert 'accolades' in data
        assert 10 in data['accolades']

    def test_get_leaderboard(self):
        """Test getting the leaderboard"""
        student1 = create_student("studenttest9", "password", "Student Test 9")
        student2 = create_student("studenttest10", "password", "Student Test 10")
        add_hours_to_student(student1.id, 20)
        add_hours_to_student(student2.id, 30)

        app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
        client = app.test_client()

        headers = get_auth_headers(client, 'studenttest9', 'password')

        response = client.get('/api/leaderboard', headers=headers)

        assert response.status_code == 200
        leaderboard = response.json
        assert isinstance(leaderboard, list)
        if len(leaderboard) >= 2:
            student10_hours = None
            student9_hours = None
            for entry in leaderboard:
                if entry['username'] == 'studenttest10':
                    student10_hours = entry['total_hours']
                if entry['username'] == 'studenttest9':
                    student9_hours = entry['total_hours']

            if student10_hours and student9_hours:
                student10_index = next(i for i, s in enumerate(leaderboard) if s['username'] == 'studenttest10')
                student9_index = next(i for i, s in enumerate(leaderboard) if s['username'] == 'studenttest9')
                assert student10_index < student9_index


