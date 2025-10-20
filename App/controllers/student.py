from App.models import Student
from App.database import db


def create_student(username, password, name):
    """Create a new student"""
    new_student = Student(username=username, password=password, name=name)
    db.session.add(new_student)
    db.session.commit()
    return new_student


def get_student(student_id):
    """Get student by ID"""
    return Student.query.get(student_id)


def get_student_by_username(username):
    """Get student by username"""
    return Student.query.filter_by(username=username).first()


def get_all_students():
    """Get all students"""
    return Student.query.all()


def get_all_students_json():
    """Get all students as JSON"""
    students = Student.query.all()
    return [student.get_json() for student in students]


def add_hours_to_student(student_id, hours):
    """Add hours to a student's record"""
    student = get_student(student_id)
    if not student:
        return None
    student.add_hours(hours)
    db.session.commit()
    return student


def request_hours_confirmation(student_id):
    """Student requests confirmation of their hours"""
    student = get_student(student_id)
    if not student:
        return None
    student.request_confirmation()
    db.session.commit()
    return student


def get_student_accolades(student_id):
    """Get accolades for a student"""
    student = get_student(student_id)
    if not student:
        return None
    return student.get_accolades()


def get_leaderboard():
    """Get leaderboard sorted by hours (descending)"""
    students = Student.query.order_by(Student.total_hours.desc()).all()
    return [student.get_json() for student in students]
