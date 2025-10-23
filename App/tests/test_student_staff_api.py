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
class StudentStaffUnitTests(unittest.TestCase):

    def test_student_creation(self):
        """Test student model creation"""
        student = Student("teststudent", "password", "Test Student")
        assert student.username == "teststudent"
        assert student.name == "Test Student"
        assert student.total_hours == 0
        assert student.confirmation_requested == False

    def test_staff_creation(self):
        """Test staff model creation"""
        staff = Staff("teststaff", "password", "Test Staff")
        assert staff.username == "teststaff"
        assert staff.name == "Test Staff"

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

# This fixture creates an empty database for the test and deletes it after the test
@pytest.fixture(autouse=True, scope="module")
def empty_db():
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
    create_db()
    yield app.test_client()
    db.drop_all()


class StudentAPIIntegrationTests(unittest.TestCase):

    def test_get_students_as_staff(self):
        """Test getting all students as staff member"""
        # Create a staff member and student
        staff = create_staff("stafftest1", "password", "Staff Test")
        student = create_student("studenttest1", "password", "Student Test")
        
        app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
        client = app.test_client()
        
        # Login as staff and get auth headers
        headers = get_auth_headers(client, 'stafftest1', 'password')
        
        # Get all students
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
        
        # Login as student
        headers = get_auth_headers(client, 'studenttest2', 'password')
        # Try to get all students (should be forbidden)

        response = client.get('/api/students', headers=headers)
        
        assert response.status_code == 403

    def test_get_student_by_id(self):
        """Test getting a specific student by ID"""
        student = create_student("studenttest3", "password", "Student Test 3")
        
        app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
        client = app.test_client()
        
        # Login as the student
        headers = get_auth_headers(client, 'studenttest3', 'password')
        # Get student by ID

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
        
        # Login as student1
        headers = get_auth_headers(client, 'studenttest4', 'password')
        # Try to get student2's details

        response = client.get(f'/api/students/{student2.id}', headers=headers)
        
        assert response.status_code == 403

    def test_get_current_student(self):
        """Test getting current student's profile"""
        student = create_student("studenttest6", "password", "Student Test 6")
        
        app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
        client = app.test_client()
        
        # Login as student
        headers = get_auth_headers(client, 'studenttest6', 'password')
        # Get current student profile

        response = client.get('/api/students/me', headers=headers)
        
        assert response.status_code == 200
        data = response.json
        assert data['username'] == 'studenttest6'

    def test_request_hours_confirmation(self):
        """Test student requesting hours confirmation"""
        student = create_student("studenttest7", "password", "Student Test 7")
        
        app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
        client = app.test_client()
        
        # Login as student
        headers = get_auth_headers(client, 'studenttest7', 'password')
        # Request confirmation

        response = client.post('/api/students/me/request-confirmation', headers=headers)
        
        assert response.status_code == 200
        data = response.json
        assert 'message' in data
        assert data['student']['confirmation_requested'] == True

    def test_get_student_accolades(self):
        """Test getting student accolades"""
        student = create_student("studenttest8", "password", "Student Test 8")
        # Add some hours to get accolades
        add_hours_to_student(student.id, 15)
        
        app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
        client = app.test_client()
        
        # Login as student
        headers = get_auth_headers(client, 'studenttest8', 'password')
        # Get accolades

        response = client.get(f'/api/students/{student.id}/accolades', headers=headers)
        
        assert response.status_code == 200
        data = response.json
        assert 'accolades' in data
        assert 10 in data['accolades']  # Should have 10-hour accolade

    def test_get_leaderboard(self):
        """Test getting the leaderboard"""
        student1 = create_student("studenttest9", "password", "Student Test 9")
        student2 = create_student("studenttest10", "password", "Student Test 10")
        add_hours_to_student(student1.id, 20)
        add_hours_to_student(student2.id, 30)
        
        app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
        client = app.test_client()
        
        # Login as student
        headers = get_auth_headers(client, 'studenttest9', 'password')
        # Get leaderboard

        response = client.get('/api/leaderboard', headers=headers)
        
        assert response.status_code == 200
        leaderboard = response.json
        assert isinstance(leaderboard, list)
        # Leaderboard should be sorted by hours (descending)
        if len(leaderboard) >= 2:
            # Find our test students in the leaderboard
            student10_hours = None
            student9_hours = None
            for entry in leaderboard:
                if entry['username'] == 'studenttest10':
                    student10_hours = entry['total_hours']
                if entry['username'] == 'studenttest9':
                    student9_hours = entry['total_hours']
            
            if student10_hours and student9_hours:
                # Student 10 should be ranked higher (has more hours)
                student10_index = next(i for i, s in enumerate(leaderboard) if s['username'] == 'studenttest10')
                student9_index = next(i for i, s in enumerate(leaderboard) if s['username'] == 'studenttest9')
                assert student10_index < student9_index


class StaffAPIIntegrationTests(unittest.TestCase):

    def test_get_staff_as_staff(self):
        """Test getting all staff members as staff"""
        staff = create_staff("stafftest2", "password", "Staff Test 2")
        
        app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
        client = app.test_client()
        
        # Login as staff
        headers = get_auth_headers(client, 'stafftest2', 'password')
        # Get all staff

        response = client.get('/api/staff', headers=headers)
        
        assert response.status_code == 200
        staff_list = response.json
        assert isinstance(staff_list, list)

    def test_get_staff_as_student_forbidden(self):
        """Test that students cannot view staff list"""
        student = create_student("studenttest11", "password", "Student Test 11")
        
        app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
        client = app.test_client()
        
        # Login as student
        headers = get_auth_headers(client, 'studenttest11', 'password')
        # Try to get all staff (should be forbidden)

        response = client.get('/api/staff', headers=headers)
        
        assert response.status_code == 403

    def test_get_current_staff(self):
        """Test getting current staff member's profile"""
        staff = create_staff("stafftest3", "password", "Staff Test 3")
        
        app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
        client = app.test_client()
        
        # Login as staff
        headers = get_auth_headers(client, 'stafftest3', 'password')
        # Get current staff profile

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
        
        # Login as staff
        headers = get_auth_headers(client, 'stafftest4', 'password')
        # Log hours for student

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
        
        # Login as student
        headers = get_auth_headers(client, 'studenttest13', 'password')
        # Try to log hours (should be forbidden)

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
        
        # Login as student and request confirmation
        student_headers = get_auth_headers(client, 'studenttest14', 'password')
        client.post('/api/students/me/request-confirmation', headers=student_headers)
        
        # Login as staff
        staff_headers = get_auth_headers(client, 'stafftest5', 'password')
        
        # Confirm hours
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
        
        # Login as student and request confirmation
        student_headers = get_auth_headers(client, 'studenttest15', 'password')
        client.post('/api/students/me/request-confirmation', headers=student_headers)
        
        # Login as staff
        staff_headers = get_auth_headers(client, 'stafftest6', 'password')
        
        # Get pending confirmations
        response = client.get('/api/staff/pending-confirmations', headers=staff_headers)
        
        assert response.status_code == 200
        pending = response.json
        assert isinstance(pending, list)
        # Should have at least the student we just added
        student_found = any(s['username'] == 'studenttest15' for s in pending)
        assert student_found

    def test_log_hours_validation(self):
        """Test validation when logging hours"""
        staff = create_staff("stafftest7", "password", "Staff Test 7")
        
        app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
        client = app.test_client()
        
        # Login as staff
        headers = get_auth_headers(client, 'stafftest7', 'password')
        
        # Try to log hours without student_id
        response = client.post('/api/staff/log-hours',
            data=json.dumps({'hours': 10}),
            headers=headers,
            content_type='application/json'
        )
        
        assert response.status_code == 400
        
        # Try to log hours with invalid student_id
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
        
        # Login as staff
        staff_headers = get_auth_headers(client, 'stafftest8', 'password')
        
        # Log 25 hours for student
        client.post('/api/staff/log-hours',
            data=json.dumps({'student_id': student.id, 'hours': 25}),
            headers=staff_headers,
            content_type='application/json'
        )
        
        # Login as student to check accolades
        student_headers = get_auth_headers(client, 'studenttest16', 'password')
        
        # Get accolades
        response = client.get(f'/api/students/{student.id}/accolades', headers=student_headers)
        
        assert response.status_code == 200
        data = response.json
        assert 10 in data['accolades']  # 10-hour milestone
        assert 25 in data['accolades']  # 25-hour milestone
