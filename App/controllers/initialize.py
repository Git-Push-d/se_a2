from .user import create_user
from .student import create_student
from .staff import create_staff
from App.database import db


def initialize():
    db.drop_all()
    db.create_all()

    student1 = create_student('alice', 'alice123', 'Alice Johnson')
    student2 = create_student('bob', 'bob123', 'Bob Smith')
    student3 = create_student('charlie', 'charlie123', 'Charlie Brown')

    staff1 = create_staff('staff1', 'staff123', 'Mr. Johnson')
    staff2 = create_staff('staff2', 'staff456', 'Ms. Davis')

    print('Database initialized with sample data!')
    print(f'Students created: {student1.username}, {student2.username}, {student3.username}')
    print(f'Staff created: {staff1.username}, {staff2.username}')
