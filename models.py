from typing import List

class User:
    def __init__(self, user_id: int, name: str, username: str, password: str):
        self.id = user_id
        self.name = name
        self.username = username
        self.password = password  

    def login(self, password: str) -> bool:
        return self.password == password #verify


class Student(User):
    def __init__(self, user_id: int, name: str, username: str, password: str):
        super().__init__(user_id, name, username, password)#inherit from user
        self.total_hours = 0
        self.accolades: List[int] = [] #for accolades
        self.confirmation_requested = False

    def add_hours(self, hours: int):
        if hours <= 0:
            raise ValueError("Hours must be positive.")
        self.total_hours += hours
        self._check_accolades()

    def _check_accolades(self):
        milestones = [10, 25, 50]
        for milestone in milestones:
            if self.total_hours >= milestone and milestone not in self.accolades:
                self.accolades.append(milestone)

    def request_confirmation(self):
        self.confirmation_requested = True

    def view_accolades(self) -> List[int]:
        return self.accolades


class Staff(User):
    def log_hours(self, student: Student, hours: int):
        student.add_hours(hours)

    def confirm_hours(self, student: Student):
        if student.confirmation_requested:
            student.confirmation_requested = False
            return True
        return False