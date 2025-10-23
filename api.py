import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from App import db
from App.models import User  # Your SQLAlchemy User model
from system import CommunityServiceTracker
from werkzeug.security import generate_password_hash, check_password_hash

# ------------------ FLASK APP SETUP ------------------
app = Flask(__name__)
CORS(app)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/database.db'  # adjust path if needed
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize db with app
db.init_app(app)

# Initialize your system
system = CommunityServiceTracker()


# ------------------ HELPER FUNCTIONS ------------------
def create_bob_if_missing():
    existing_user = User.query.filter_by(username="bob").first()
    if not existing_user:
        bob = User(
            username="bob",
            password=generate_password_hash("bobpass"),
            name="Bob",
            user_type="user"
        )
        db.session.add(bob)
        db.session.commit()


def get_user_by_token(token):
    """Return user object based on token (username simulation)."""
    if not token:
        return None
    return User.query.filter_by(username=token).first()


# ------------------ ROUTES ------------------
@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        token = username  # simple token for demo
        return jsonify({"access_token": token})
    return jsonify({"error": "Invalid credentials"}), 401


@app.route("/api/identify", methods=["GET"])
def identify():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = get_user_by_token(token)
    if user:
        return jsonify({"username": user.username, "role": user.user_type})
    return jsonify({"error": "Unauthorized"}), 401


@app.route("/api/students/me/request-confirmation", methods=["POST"])
def request_confirmation():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    student = get_user_by_token(token)
    if student and student.user_type == "user":
        s = system.get_student_by_name(student.username)
        if s:
            s.request_confirmation()
            return jsonify({"message": "Hours confirmation requested"})
    return jsonify({"error": "Unauthorized"}), 401


@app.route("/api/staff/log-hours", methods=["POST"])
def log_hours():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    staff = get_user_by_token(token)
    if not staff or staff.user_type != "staff":
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    student_id = data.get("student_id")
    hours = data.get("hours")
    student = system.get_student(student_id)
    if not student:
        return jsonify({"error": "Student not found"}), 404

    staff_obj = system.get_staff_by_name(staff.username)
    staff_obj.log_hours(student, hours)
    return jsonify({"message": f"Logged {hours} hours for {student.name}"})


@app.route("/api/leaderboard", methods=["GET"])
def leaderboard():
    board = [{"name": s.name, "hours": s.hours} for s in sorted(system.students, key=lambda x: x.hours, reverse=True)]
    return jsonify(board)


# ------------------ MAIN -------------


