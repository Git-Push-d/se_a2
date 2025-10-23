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
class StaffUnitTests(unittest.TestCase):

    def test_staff_creation(self):
        """Test staff model creation"""
        staff = Staff("teststaff", "password", "Test Staff")
        assert staff.username == "teststaff"
        assert staff.name == "Test Staff"


'''
    Integration Tests
'''

@pytest.fixture(autouse=True, scope="module")
def empty_db():
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
    create_db()
    yield app.test_client()
    db.drop_all()


class StaffAPIIntegrationTests(unittest.TestCase):

    def test_get_staff_as_staff(self):
        """Test getting all staff members as staff"""
        staff = create_staff("stafftest2", "password", "Staff Test 2")
        
        app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
        client = app.test_client()
        
        headers = get_auth_headers(client, 'stafftest2', 'password')

        response = client.get('/api/staff', headers=headers)
        
        assert response.status_code == 200
        staff_list = response.json
        assert isinstance(staff_list, list)

    def test_get_staff_as_student_forbidden(self):
        """Test that students cannot view staff list"""
        student = create_student("studenttest11", "password", "Student Test 11")
        
        app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
        client = app.test_client()
        
        headers = get_auth_headers(client, 'studenttest11', 'password')

        response = client.get('/api/staff', headers=headers)
        
        assert response.status_code == 403

    def test_get_current_staff(self):
        """Test getting current staff member's profile"""
        staff = create_staff("stafftest3", "password", "Staff Test 3")
        
        app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
        client = app.test_client()
        
        headers = get_auth_headers(client, 'stafftest3', 'password')

        response = client.get('/api/staff/me', headers=headers)
        
        assert response.status_code == 200
        data = response.json
        assert data['username'] == 'stafftest3'

    def test_staff_log_hours_for_student(self):
        """Test staff logging hours for a student"""
        staff = create_staff("stafftest4", "password", "Staff Test 4")
        student = create_student("studenttest12", "password", "Student Test 12")
        
        app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
        client = app.test_client()
        
        headers = get_auth_headers(client, 'stafftest4', 'password')

        response = client.post('/api/staff/log-hours',
            data=json.dumps({'student_id': student.id, 'hours': 10}),
            headers=headers,
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.json
        assert 'message' in data
        assert data['student']['total_hours'] == 10

    def test_student_cannot_log_hours(self):
        """Test that students cannot log hours"""
        student = create_student("studenttest13", "password", "Student Test 13")
        
        app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
        client = app.test_client()
        
        headers = get_auth_headers(client, 'studenttest13', 'password')

        response = client.post('/api/staff/log-hours',
            data=json.dumps({'student_id': 1, 'hours': 10}),
            headers=headers,
            content_type='application/json'
        )
        
        assert response.status_code == 403

    def test_staff_confirm_hours(self):
        """Test staff confirming student hours"""
        staff = create_staff("stafftest5", "password", "Staff Test 5")
        student = create_student("studenttest14", "password", "Student Test 14")
        
        app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
        client = app.test_client()
        
        student_headers = get_auth_headers(client, 'studenttest14', 'password')
        client.post('/api/students/me/request-confirmation', headers=student_headers)
        
        staff_headers = get_auth_headers(client, 'stafftest5', 'password')
        
        response = client.post('/api/staff/confirm-hours',
            data=json.dumps({'student_id': student.id}),
            headers=staff_headers,
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.json
        assert 'message' in data
        assert data['student']['confirmation_requested'] == False

    def test_get_pending_confirmations(self):
        """Test getting pending confirmation requests"""
        staff = create_staff("stafftest6", "password", "Staff Test 6")
        student = create_student("studenttest15", "password", "Student Test 15")
        
        app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
        client = app.test_client()
        
        student_headers = get_auth_headers(client, 'studenttest15', 'password')
        client.post('/api/students/me/request-confirmation', headers=student_headers)
        
        staff_headers = get_auth_headers(client, 'stafftest6', 'password')
        
        response = client.get('/api/staff/pending-confirmations', headers=staff_headers)
        
        assert response.status_code == 200
        pending = response.json
        assert isinstance(pending, list)
        student_found = any(s['username'] == 'studenttest15' for s in pending)
        assert student_found

    def test_log_hours_validation(self):
        """Test validation when logging hours"""
        staff = create_staff("stafftest7", "password", "Staff Test 7")
        
        app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
        client = app.test_client()
        
        headers = get_auth_headers(client, 'stafftest7', 'password')
        
        response = client.post('/api/staff/log-hours',
            data=json.dumps({'hours': 10}),
            headers=headers,
            content_type='application/json'
        )
        
        assert response.status_code == 400
        
        response = client.post('/api/staff/log-hours',
            data=json.dumps({'student_id': 99999, 'hours': 10}),
            headers=headers,
            content_type='application/json'
        )
        
        assert response.status_code == 400

    def test_accolade_milestones(self):
        """Test that accolades are awarded at correct milestones"""
        staff = create_staff("stafftest8", "password", "Staff Test 8")
        student = create_student("studenttest16", "password", "Student Test 16")
        
        app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
        client = app.test_client()
        
        staff_headers = get_auth_headers(client, 'stafftest8', 'password')
        
        client.post('/api/staff/log-hours',
            data=json.dumps({'student_id': student.id, 'hours': 25}),
            headers=staff_headers,
            content_type='application/json'
        )
        
        student_headers = get_auth_headers(client, 'studenttest16', 'password')
        
        response = client.get(f'/api/students/{student.id}/accolades', headers=student_headers)
        
        assert response.status_code == 200
        data = response.json
        assert 10 in data['accolades']
        assert 25 in data['accolades']
