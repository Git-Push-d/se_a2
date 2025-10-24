# Unit Test Plan - Community Service Tracker

This document outlines all automated unit and integration tests implemented in the codebase.

---

## Authentication Tests (test_auth_api.py)

| Test ID | Test Name | Input | Expected Output |
|---------|-----------|-------|-----------------|
| UT-01 | Valid User Login (API) | username = "logintest"<br>password = "password123" | login_success = True<br>response.status_code = 200<br>access_token = present |
| UT-02 | Invalid Username Login | username = "nonexistent"<br>password = "password123" | login_success = False<br>response.status_code = 401<br>error_message = "bad username or password" |
| UT-03 | Invalid Password Login | username = "passtest"<br>password = "wrongpass" | login_success = False<br>response.status_code = 401<br>error_message = "bad username or password" |
| UT-04 | Valid Student Login (API) | username = "studenttest"<br>password = "studentpass"<br>role = "Student" | login_success = True<br>response.status_code = 200<br>access_token = present |
| UT-05 | Valid Staff Login (API) | username = "stafftest"<br>password = "staffpass"<br>role = "Staff" | login_success = True<br>response.status_code = 200<br>access_token = present |
| UT-06 | Login Missing Credentials | username = "testuser"<br>password = None | login_success = False<br>response.status_code = 400/401/500 |
| UT-07 | Identify with Valid Token | Authorization header with JWT token | response.status_code = 200<br>user_info = returned |
| UT-08 | Identify without Token | No Authorization header | response.status_code = 401<br>unauthorized = True |
| UT-09 | Logout API | GET /api/logout | response.status_code = 200<br>message = "logged out" |
| UT-10 | Token Persistence | JWT token used across multiple requests | All requests succeed<br>Same user info returned |
| UT-11 | Password Hashing | password = "testpass123"<br>user = User(...) | hashed_password ≠ plaintext_password<br>check_password() = True |
| UT-12 | Password Validation | correct_password vs wrong_password | correct = True<br>wrong = False |

---

## Student Tests (test_student_api.py)

### Student Model Unit Tests

| Test ID | Test Name | Input | Expected Output |
|---------|-----------|-------|-----------------|
| UT-13 | Student Creation | username = "teststudent"<br>password = "password"<br>name = "Test Student" | student.username = "teststudent"<br>student.total_hours = 0<br>confirmation_requested = False |
| UT-14 | Student Add Hours | student.add_hours(5)<br>student.add_hours(3) | total_hours = 5 (after first)<br>total_hours = 8 (after second) |
| UT-15 | Student Request Confirmation | student.request_confirmation() | confirmation_requested = False → True |

### Student API Integration Tests

| Test ID | Test Name | Input | Expected Output |
|---------|-----------|-------|-----------------|
| UT-16 | Get All Students (Staff) | Logged in as staff<br>GET /api/students | response.status_code = 200<br>students = list<br>len(students) > 0 |
| UT-17 | Get Students (Student - Forbidden) | Logged in as student<br>GET /api/students | response.status_code = 403<br>access_denied = True |
| UT-18 | Get Student by ID | Logged in as student<br>GET /api/students/{id} | response.status_code = 200<br>student_data = returned |
| UT-19 | Get Another Student (Unauthorized) | Logged in as student1<br>GET /api/students/{student2_id} | response.status_code = 403<br>access_denied = True |
| UT-20 | Get Current Student Profile | Logged in as student<br>GET /api/students/me | response.status_code = 200<br>username = "studenttest6"<br>profile_data = returned |
| UT-21 | Request Hours Confirmation (API) | Logged in as student<br>POST /api/students/me/request-confirmation | response.status_code = 200<br>confirmation_requested = True<br>message = present |
| UT-22 | Get Student Accolades | student_hours = 15<br>GET /api/students/{id}/accolades | response.status_code = 200<br>accolades = [10]<br>10-hour badge = awarded |
| UT-23 | Get Leaderboard | students with 20 and 30 hours<br>GET /api/leaderboard | response.status_code = 200<br>leaderboard = sorted by hours DESC<br>highest_hours_first = True |

---

## Staff Tests (test_staff_api.py)

### Staff Model Unit Tests

| Test ID | Test Name | Input | Expected Output |
|---------|-----------|-------|-----------------|
| UT-24 | Staff Creation | username = "teststaff"<br>password = "password"<br>name = "Test Staff" | staff.username = "teststaff"<br>staff.name = "Test Staff" |

### Staff API Integration Tests

| Test ID | Test Name | Input | Expected Output |
|---------|-----------|-------|-----------------|
| UT-25 | Get All Staff (Staff) | Logged in as staff<br>GET /api/staff | response.status_code = 200<br>staff_list = list |
| UT-26 | Get Staff (Student - Forbidden) | Logged in as student<br>GET /api/staff | response.status_code = 403<br>access_denied = True |
| UT-27 | Get Current Staff Profile | Logged in as staff<br>GET /api/staff/me | response.status_code = 200<br>username = "stafftest3"<br>profile_data = returned |
| UT-28 | Staff Log Hours for Student | Logged in as staff<br>POST /api/staff/log-hours<br>student_id = 12<br>hours = 10 | response.status_code = 200<br>student.total_hours = 10<br>message = "Hours logged successfully" |
| UT-29 | Student Cannot Log Hours | Logged in as student<br>POST /api/staff/log-hours | response.status_code = 403<br>access_denied = True |
| UT-30 | Staff Confirm Hours | Student requested confirmation<br>Logged in as staff<br>POST /api/staff/confirm-hours<br>student_id = 14 | response.status_code = 200<br>confirmation_requested = False<br>message = present |
| UT-31 | Get Pending Confirmations | Student requested confirmation<br>Logged in as staff<br>GET /api/staff/pending-confirmations | response.status_code = 200<br>pending_list = contains student<br>student_found = True |
| UT-32 | Log Hours Validation (Missing Student ID) | POST /api/staff/log-hours<br>student_id = None<br>hours = 10 | response.status_code = 400<br>validation_error = True |
| UT-33 | Log Hours Validation (Invalid Student ID) | POST /api/staff/log-hours<br>student_id = 99999<br>hours = 10 | response.status_code = 400<br>student_not_found = True |
| UT-34 | Accolade Milestones | Staff logs 25 hours for student<br>GET /api/students/{id}/accolades | response.status_code = 200<br>accolades = [10, 25]<br>both_badges_awarded = True |

---

## Test Summary

- **Total Tests:** 34
- **Authentication Tests:** 12
- **Student Tests:** 11 (3 unit + 8 integration)
- **Staff Tests:** 11 (1 unit + 10 integration)

---

## Test Coverage

### Authentication & Authorization
- ✅ Valid/Invalid login credentials
- ✅ Role-based login (Student/Staff)
- ✅ JWT token generation and validation
- ✅ Password hashing and verification
- ✅ Token persistence across requests
- ✅ Unauthorized access handling

### Student Functionality
- ✅ Student model creation and properties
- ✅ Adding hours to student records
- ✅ Requesting hour confirmations
- ✅ Viewing own profile
- ✅ Role-based access control (students cannot view all students)
- ✅ Accolade badge awards at milestones
- ✅ Leaderboard ranking by hours

### Staff Functionality
- ✅ Staff model creation
- ✅ Logging hours for students
- ✅ Confirming student hour requests
- ✅ Viewing pending confirmations
- ✅ Input validation for logging hours
- ✅ Role-based access control (students cannot log hours)
- ✅ Accolade milestone verification

### Security & Access Control
- ✅ Students cannot access staff-only endpoints (403)
- ✅ Students cannot view other students' details (403)
- ✅ Students cannot log hours (403)
- ✅ Requests without tokens are rejected (401)
- ✅ Invalid credentials return proper errors (401)

---

## Running Tests

```bash
# Run all tests
cd App/tests
python -m pytest -v

# Run specific test file
python -m pytest test_auth_api.py -v
python -m pytest test_student_api.py -v
python -m pytest test_staff_api.py -v

# Run with coverage
python -m pytest --cov=App --cov-report=html
```

---

## Test Credentials

**Students:**
- joe / 1234 (student_id: 10)
- alice / alice123 (student_id: 1)
- bob / bob123
- charlie / charlie123

**Staff:**
- staff5 / 5678
- staff1 / staff123

---

*Last Updated: October 24, 2025*
