# Postman Testing Guide - Step by Step

## Important: Login First!

You MUST login before testing any other endpoints. The token determines whether you're a student or staff.

---

## Test 1: Student Workflow

### Step 1: Login as Student
**Endpoint:** `Login (Student)`
- Click "Send"
- ✅ Should return `access_token`
- Token is automatically saved

### Step 2: Get Your Profile
**Endpoint:** `Get Current Student`
- Click "Send"
- ✅ Should show joe's profile with total_hours, accolades, etc.

### Step 3: Request Confirmation
**Endpoint:** `Request Hours Confirmation`
- Click "Send"
- ✅ Should show `confirmation_requested: true`

### Step 4: View Leaderboard
**Endpoint:** `Get Leaderboard`
- Click "Send"
- ✅ Should show all students ranked by hours

---

## Test 2: Staff Workflow

### Step 1: Login as Staff
**Endpoint:** `Login (Staff)`
- Click "Send"
- ✅ Should return `access_token`
- Token is automatically saved (overwrites student token!)

### Step 2: Get Your Profile
**Endpoint:** `Get Current Staff Profile`
- Click "Send"
- ✅ Should show staff5's profile

### Step 3: View All Students
**Endpoint:** `Get All Students (Staff Only)`
- Click "Send"
- ✅ Should show list of all students

### Step 4: Log Hours for Joe
**Endpoint:** `Log Hours for Student`
- Body already set to: `{"student_id": 10, "hours": 10}`
- Click "Send"
- ✅ Should add 10 hours to joe

### Step 5: View Pending Confirmations
**Endpoint:** `Get Pending Confirmations`
- Click "Send"
- ✅ Should show students who requested confirmation

### Step 6: Confirm Joe's Hours
**Endpoint:** `Confirm Student Hours`
- Body already set to: `{"student_id": 10}`
- Click "Send"
- ✅ Should mark joe's confirmation as complete

---

## Common Mistakes

### ❌ Testing student endpoints while logged in as staff
**Error:** 403 Forbidden - "User is not a student"
**Fix:** Login as student first using `Login (Student)`

### ❌ Testing staff endpoints while logged in as student
**Error:** 403 Forbidden - "Unauthorized"
**Fix:** Login as staff first using `Login (Staff)`

### ❌ Using old token
**Error:** 401 Unauthorized - "Missing JWT"
**Fix:** Login again to get a fresh token

---

## Pro Tips

1. **Always check which user you're logged in as**
   - Use `Identify Current User` endpoint
   - Returns your username and ID

2. **Token expires after 15 minutes**
   - Just login again if you get 401 errors

3. **Each login overwrites the previous token**
   - If you login as staff, you're no longer logged in as student
   - Need to switch? Just login as the other role again

---

## Quick Test Sequence

**Full workflow in order:**
1. Login (Student) → joe
2. Request Hours Confirmation → joe requests
3. Login (Staff) → staff5 (overwrites joe's token)
4. View Pending Confirmations → see joe's request
5. Confirm Student Hours → approve joe
6. Login (Student) → joe again
7. Get Current Student → see confirmation is now false

This proves the full workflow works! 🎉
