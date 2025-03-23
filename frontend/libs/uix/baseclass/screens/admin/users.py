from kivy.clock import Clock
from kivy.clock import _default_time as time
from kivy.properties import ListProperty
from kivymd.uix.screen import MDScreen
from libs.applibs.generated_connection_manager import StudentsRoutes
from libs.uix.baseclass.components.user_view_list import UserViewListItem


class UsersScreen(MDScreen):
    students = ListProperty([])

    def on_pre_enter(self):
        self.get_all_students()
        # Clear current displayed list
        self.ids.user_list.clear_widgets()

    def on_enter(self):
        self.show_loading()
        Clock.schedule_interval(self.update_ui_with_students, 0)

    def show_loading(self):
        # Implement loading UI (e.g., spinner) if needed
        pass

    def hide_loading(self):
        # Hide loading UI when data is loaded
        pass

    def get_all_students(self):
        # Fetch students from the server
        response = StudentsRoutes(client=self.manager.connection_client).get_students()

        # Stop the loading animation when response is received
        self.hide_loading()

        if response.status_code != 200:
            print("Failed to get Users")
            return

        students = response.json()
        self.students = students
        # Cache the students for future filtering
        self.manager.set_shared_data("cached_students", students)

    def update_ui_with_students(self, *args) -> None:
        # Limit the update to 60 FPS to avoid blocking the UI
        limit = Clock.get_time() + 1 / 60
        while self.students and time() < limit:
            student = self.students.pop(0)
            self.add_user_item(student)

    def add_user_item(self, user):
        """Helper function to add a user item to the UI"""

        user_item = UserViewListItem(
            fullname=f"{user.get('first_name')} {user.get('last_name')}",
            email=f"{user.get('email')}",
            phone_number=f"{user.get('phone_number')}",
        )

        # Bind the on_click event to the student item
        user_item.bind(
            on_release=lambda instance, student=user: self.load_student_details(student)
        )

        # Add the user item to the UI
        self.ids.user_list.add_widget(user_item)

    def load_student_details(self, student: dict) -> None:
        # Set the current student details in shared data
        self.manager.set_shared_data("current_student", student)
        self.manager.set_shared_data("current_student_id", student.get("id"))
        print(self.manager.get_shared_data("current_student_id"))
        # Navigate to the student details screen
        self.manager.push("account_details")

    def profile(self):
        self.manager.push("profile")
