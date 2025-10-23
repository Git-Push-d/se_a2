# Postman API Testing Guide

## Quick Start

### 1. Import the Collection
1. Open Postman
2. Click "Import" button
3. Select `CommunityTracker_Postman_Collection.json`
4. The collection will be imported with all endpoints

### 2. Start the Server
```bash
python3 run.py
```
Server will run on `http://localhost:5000`

### 3. Test the API

#### Step 1: Login
1. In Postman, open the collection
2. Go to **Authentication → Login (Student)** or **Login (Staff)**
3. Click "Send"
4. The JWT token will be automatically saved for subsequent requests

#### Step 2: Make Authenticated Requests
1. All other endpoints will automatically use the saved token
2. The `Authorization: Bearer <token>` header is added automatically
3. Test any endpoint - no manual token management needed!

## How It Works

### Authentication Flow
1. **Login Request** → Returns `access_token` in JSON response
2. **Token Saved** → Postman test script saves it to collection variable
3. **Auto-Applied** → All requests use `{{token}}` variable in Authorization header

### Example: Complete Workflow

**Test as Student:**
```
1. Login (Student) with username: alice, password: password
2. Get Current Student Profile → /api/students/me
3. Request Hours Confirmation → /api/students/me/request-confirmation
4. View Leaderboard → /api/leaderboard
```

**Test as Staff:**
```
1. Login (Staff) with username: staff1, password: password
2. Get All Students → /api/students
3. Log Hours → /api/staff/log-hours
   Body: {"student_id": 1, "hours": 10}
4. Get Pending Confirmations → /api/staff/pending-confirmations
5. Confirm Hours → /api/staff/confirm-hours
   Body: {"student_id": 1}
```

## Important Notes

### ✅ What Changed for Postman Compatibility
- **Before**: API used cookie-based authentication (CSRF tokens required)
- **After**: API uses `Authorization: Bearer <token>` headers
- **Result**: Works perfectly with Postman and all API clients!

### 🔑 Authorization Header
All protected endpoints require:
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```
The Postman collection handles this automatically!

### 📝 Sample Credentials
**Students:**
- alice / password
- bob / password
- charlie / password

**Staff:**
- staff1 / password
- staff2 / password

## Troubleshooting

### "Missing JWT" Error
- Make sure you've logged in first
- Check that the token variable is set (View → Collection Variables)
- Try logging in again

### "Unauthorized" Error
- Token may have expired (default: 7 days)
- Login again to get a new token

### Server Not Running
- Ensure `python3 run.py` is running
- Check server is on `http://localhost:5000`
- Verify no firewall blocking port 5000

## API Endpoints Summary

### Authentication (3)
- POST `/api/login` - Get JWT token
- GET `/api/identify` - Check current user
- GET `/api/logout` - Logout (discard token)

### Student Endpoints (6)
- GET `/api/students` - All students (staff only)
- GET `/api/students/<id>` - Get student by ID
- GET `/api/students/me` - Current student profile
- POST `/api/students/me/request-confirmation` - Request confirmation
- GET `/api/students/<id>/accolades` - View accolades
- GET `/api/leaderboard` - View leaderboard

### Staff Endpoints (5)
- GET `/api/staff` - All staff (staff only)
- GET `/api/staff/me` - Current staff profile
- POST `/api/staff/log-hours` - Log hours for student
- POST `/api/staff/confirm-hours` - Confirm student hours
- GET `/api/staff/pending-confirmations` - View pending requests

##Happy Testing! 🚀
