# system.py

from models import Student, Staff

class CommunityServiceTracker:
    """Main system class that manages students, staff, and authentication."""

    def __init__(self):
        self.students = []  # List of Student objects
        self.staff_members = []  # List of Staff objects
        self._next_user_id = 1  # Auto-incrementing ID for users
        self._populate_sample_data()

    def _populate_sample_data(self):
        """Optional: Add some initial users for testing."""
        s1 = Student(self._next_user_id, "Alice", "alice123", "pass1")
        self._next_user_id += 1
        s2 = Student(self._next_user_id, "Bob", "bob123", "pass2")
        self._next_user_id += 1

        st1 = Staff(self._next_user_id, "Mr. Smith", "smith", "admin1")
        self._next_user_id += 1

        self.students.extend([s1, s2])
        self.staff_members.append(st1)

    def add_student(self, name, username, password):
        """Add a new student to the system."""
        student = Student(self._next_user_id, name, username, password)
        self._next_user_id += 1
        self.students.append(student)
        return student

    def add_staff(self, name, username, password):
        """Add a new staff member to the system."""
        staff = Staff(self._next_user_id, name, username, password)
        self._next_user_id += 1
        self.staff_members.append(staff)
        return staff

    def get_student(self, student_id):
        """Retrieve a student by ID."""
        for student in self.students:
            if student.id == student_id:
                return student
        return None

    def view_leaderboard(self):
        """Return students sorted by total_hours in descending order."""
        def get_hours(student):
            return student.total_hours
        return sorted(self.students, key=get_hours, reverse=True)

    def display_leaderboard(self):
        """Prints the leaderboard in a nice format."""
        leaderboard = self.view_leaderboard()

        if not leaderboard:
            print("\n=== Community Service Leaderboard ===")
            print("No students have logged hours yet.\n")
            return

        print("\n=== Community Service Leaderboard ===")
        for i, student in enumerate(leaderboard, start=1):
            print(f"{i}. {student.name} - {student.total_hours} hours")
        print()

    def authenticate_user(self, username, password):
        """Check if a username/password belongs to a student or staff."""
        # Check students
        for student in self.students:
            if student.username == username and student.login(password):
                return student

        # Check staff
        for staff in self.staff_members:
            if staff.username == username and staff.login(password):
                return staff

        return None  # No match found
