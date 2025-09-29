from system import CommunityServiceTracker

def student_menu(system, student):
    while True:
        print(f"\nWelcome, {student.name}! (Student)")
        print("1. Request Hours Confirmation")
        print("2. View Accolades")
        print("3. View Leaderboard")
        print("4. Logout")
        choice = input("Enter choice: ")

        if choice == "1":
            student.request_confirmation()
            print("Hours confirmation request sent to staff.")
        elif choice == "2":
            accolades = student.view_accolades()
            if accolades:
                print("Your Accolades:", ", ".join(str(a) for a in accolades))
            else:
                print("You have no accolades yet")
        elif choice == "3":
            system.display_leaderboard()
        elif choice == "4":
            print("Logging out...")
            break
        else:
            print("Invalid choice. Please try again.")


def staff_menu(system, staff):
    while True:
        print(f"\nWelcome, {staff.name}! (Staff)")
        print("1. Log Hours for Student")
        print("2. Confirm Student Hours")
        print("3. View Leaderboard")
        print("4. Logout")
        choice = input("Enter choice: ")

        if choice == "1":
            try:
                student_id = int(input("Enter student ID: "))
                hours = int(input("Enter hours to log: "))
                student = system.get_student(student_id)
                if student:
                    staff.log_hours(student, hours)
                    print(f"Logged {hours} hours for {student.name}.")
                else:
                    print("Student not found.")
            except ValueError:
                print("Please enter valid numbers.")

        elif choice == "2":
            pending_students = [s for s in system.students if s.confirmation_requested]
            if not pending_students:
                print("No pending confirmations.")
            else:
                for s in pending_students:
                    confirmed = staff.confirm_hours(s)
                    if confirmed:
                        print(f"Confirmed hours for {s.name}.")
    

        elif choice == "3":
            system.display_leaderboard()

        elif choice == "4":
            print("Logging out...")
            break

        else:
            print("Invalid choice. Please try again.")


def main():
    system = CommunityServiceTracker()
    print("=== Community Service Tracker ===")

    while True:
        print("--- Login ---")
        username = input("Username (or 'exit' to quit): ")
        if username.lower() == "exit":
            print("Goodbye!")
            break
        password = input("Password: ")

        user = system.authenticate_user(username, password)
        if user:
            if user.__class__.__name__ == "Student":
                student_menu(system, user)
            elif user.__class__.__name__ == "Staff":
                staff_menu(system, user)
        else:
            print("Invalid username or password. Please try again.")


if __name__ == "__main__":
    main()