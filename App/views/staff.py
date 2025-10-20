from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, current_user

from App.controllers import (
    log_hours_for_student,
    confirm_student_hours,
    get_pending_confirmations,
    get_all_staff_json
)

staff_views = Blueprint('staff_views', __name__)


@staff_views.route('/api/staff', methods=['GET'])
@jwt_required()
def get_staff_route():
    """Get all staff members"""
    if current_user.user_type != 'staff':
        return jsonify({'error': 'Unauthorized'}), 403

    staff = get_all_staff_json()
    return jsonify(staff), 200


@staff_views.route('/api/staff/me', methods=['GET'])
@jwt_required()
def get_current_staff():
    """Get current logged-in staff member's profile"""
    if current_user.user_type != 'staff':
        return jsonify({'error': 'User is not a staff member'}), 403

    return jsonify(current_user.get_json()), 200


@staff_views.route('/api/staff/log-hours', methods=['POST'])
@jwt_required()
def log_hours_route():
    """Staff logs hours for a student"""
    if current_user.user_type != 'staff':
        return jsonify({'error': 'Only staff can log hours'}), 403

    data = request.get_json()
    student_id = data.get('student_id')
    hours = data.get('hours')

    if not student_id or not hours:
        return jsonify({'error': 'student_id and hours are required'}), 400

    try:
        hours = int(hours)
    except ValueError:
        return jsonify({'error': 'Hours must be a number'}), 400

    student, error = log_hours_for_student(current_user.id, student_id, hours)
    if error:
        return jsonify({'error': error}), 400

    return jsonify({
        'message': f'Logged {hours} hours for student',
        'student': student.get_json()
    }), 200


@staff_views.route('/api/staff/confirm-hours', methods=['POST'])
@jwt_required()
def confirm_hours_route():
    """Staff confirms hours requested by student"""
    if current_user.user_type != 'staff':
        return jsonify({'error': 'Only staff can confirm hours'}), 403

    data = request.get_json()
    student_id = data.get('student_id')

    if not student_id:
        return jsonify({'error': 'student_id is required'}), 400

    student, error = confirm_student_hours(current_user.id, student_id)
    if error:
        return jsonify({'error': error}), 400

    return jsonify({
        'message': 'Hours confirmation completed',
        'student': student.get_json()
    }), 200


@staff_views.route('/api/staff/pending-confirmations', methods=['GET'])
@jwt_required()
def get_pending_confirmations_route():
    """Get all students with pending confirmation requests"""
    if current_user.user_type != 'staff':
        return jsonify({'error': 'Only staff can view pending confirmations'}), 403

    students = get_pending_confirmations()
    return jsonify(students), 200
