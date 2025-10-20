from werkzeug.security import check_password_hash, generate_password_hash
from App.database import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    user_type = db.Column(db.String(20), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': user_type
    }

    def __init__(self, username, password, name):
        self.username = username
        self.name = name
        self.set_password(password)

    def get_json(self):
        return{
            'id': self.id,
            'username': self.username,
            'name': self.name,
            'user_type': self.user_type
        }

    def set_password(self, password):
        """Create hashed password."""
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password, password)


class Student(User):
    __tablename__ = 'student'
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    total_hours = db.Column(db.Integer, default=0)
    confirmation_requested = db.Column(db.Boolean, default=False)

    accolades = db.relationship('Accolade', backref='student', lazy=True, cascade='all, delete-orphan')

    __mapper_args__ = {
        'polymorphic_identity': 'student',
    }

    def __init__(self, username, password, name):
        super().__init__(username, password, name)
        self.total_hours = 0
        self.confirmation_requested = False

    def add_hours(self, hours):
        if hours <= 0:
            raise ValueError("Hours must be positive.")
        self.total_hours += hours
        self._check_accolades()

    def _check_accolades(self):
        """Check and award accolades for milestones"""
        milestones = [10, 25, 50, 100]
        for milestone in milestones:
            if self.total_hours >= milestone:
                existing = Accolade.query.filter_by(student_id=self.id, milestone=milestone).first()
                if not existing:
                    accolade = Accolade(student_id=self.id, milestone=milestone)
                    db.session.add(accolade)

    def request_confirmation(self):
        self.confirmation_requested = True

    def get_accolades(self):
        return [a.milestone for a in self.accolades]

    def get_json(self):
        return {
            'id': self.id,
            'username': self.username,
            'name': self.name,
            'user_type': self.user_type,
            'total_hours': self.total_hours,
            'accolades': self.get_accolades(),
            'confirmation_requested': self.confirmation_requested
        }


class Staff(User):
    __tablename__ = 'staff'
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'staff',
    }

    def __init__(self, username, password, name):
        super().__init__(username, password, name)

    def get_json(self):
        return {
            'id': self.id,
            'username': self.username,
            'name': self.name,
            'user_type': self.user_type
        }


class Accolade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    milestone = db.Column(db.Integer, nullable=False)

    def __init__(self, student_id, milestone):
        self.student_id = student_id
        self.milestone = milestone

    def get_json(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'milestone': self.milestone
        }
