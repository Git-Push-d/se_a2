from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, current_user

from App.controllers import (
    get_student,
    request_hours_confirmation,
    get_student_accolades,
    get_leaderboard,
    get_all_students_json
)

student_views = Blueprint('student_views', __name__)


@student_views.route('/api/students', methods=['GET'])
@jwt_required()
def get_students_route():
    """Get all students (for staff)"""
    if current_user.user_type != 'staff':
        return jsonify({'error': 'Unauthorized'}), 403

    students = get_all_students_json()
    return jsonify(students), 200


@student_views.route('/api/students/<int:student_id>', methods=['GET'])
@jwt_required()
def get_student_route(student_id):
    """Get student details"""
    if current_user.user_type == 'student' and current_user.id != student_id:
        return jsonify({'error': 'Unauthorized'}), 403

    student = get_student(student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    return jsonify(student.get_json()), 200


@student_views.route('/api/students/me', methods=['GET'])
@jwt_required()
def get_current_student():
    """Get current logged-in student's profile"""
    if current_user.user_type != 'student':
        return jsonify({'error': 'User is not a student'}), 403

    return jsonify(current_user.get_json()), 200


@student_views.route('/api/students/me/request-confirmation', methods=['POST'])
@jwt_required()
def request_confirmation_route():
    """Student requests hours confirmation"""
    if current_user.user_type != 'student':
        return jsonify({'error': 'Only students can request confirmation'}), 403

    student = request_hours_confirmation(current_user.id)
    if not student:
        return jsonify({'error': 'Failed to request confirmation'}), 400

    return jsonify({
        'message': 'Confirmation request sent',
        'student': student.get_json()
    }), 200


@student_views.route('/api/students/<int:student_id>/accolades', methods=['GET'])
@jwt_required()
def get_accolades_route(student_id):
    """Get student accolades"""
    if current_user.user_type == 'student' and current_user.id != student_id:
        return jsonify({'error': 'Unauthorized'}), 403

    accolades = get_student_accolades(student_id)
    if accolades is None:
        return jsonify({'error': 'Student not found'}), 404

    return jsonify({'accolades': accolades}), 200


@student_views.route('/api/leaderboard', methods=['GET'])
@jwt_required()
def get_leaderboard_route():
    """Get leaderboard (all users can view)"""
    leaderboard = get_leaderboard()
    return jsonify(leaderboard), 200
