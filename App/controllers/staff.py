from App.models import Staff, Student
from App.database import db


def create_staff(username, password, name):
    """Create a new staff member"""
    new_staff = Staff(username=username, password=password, name=name)
    db.session.add(new_staff)
    db.session.commit()
    return new_staff


def get_staff(staff_id):
    """Get staff by ID"""
    return Staff.query.get(staff_id)


def get_staff_by_username(username):
    """Get staff by username"""
    return Staff.query.filter_by(username=username).first()


def get_all_staff():
    """Get all staff members"""
    return Staff.query.all()


def get_all_staff_json():
    """Get all staff as JSON"""
    staff_members = Staff.query.all()
    return [staff.get_json() for staff in staff_members]


def log_hours_for_student(staff_id, student_id, hours):
    """Staff logs hours for a student"""
    staff = get_staff(staff_id)
    if not staff:
        return None, "Staff member not found"

    student = Student.query.get(student_id)
    if not student:
        return None, "Student not found"

    if hours <= 0:
        return None, "Hours must be positive"

    student.add_hours(hours)
    db.session.commit()
    return student, None


def confirm_student_hours(staff_id, student_id):
    """Staff confirms hours requested by student"""
    staff = get_staff(staff_id)
    if not staff:
        return None, "Staff member not found"

    student = Student.query.get(student_id)
    if not student:
        return None, "Student not found"

    if not student.confirmation_requested:
        return None, "No confirmation request from this student"

    student.confirmation_requested = False
    db.session.commit()
    return student, None


def get_pending_confirmations():
    """Get all students with pending confirmation requests"""
    students = Student.query.filter_by(confirmation_requested=True).all()
    return [student.get_json() for student in students]
