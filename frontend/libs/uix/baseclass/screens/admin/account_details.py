from kivy.properties import ObjectProperty
from kivymd.uix.screen import MDScreen
from libs.applibs.generated_connection_manager import CoreRoutes, StudentsRoutes


class AccountDetailsScreen(MDScreen):
    first_name = ObjectProperty("")
    last_name = ObjectProperty("")
    email = ObjectProperty("")
    role = ObjectProperty("")
    phone_number = ObjectProperty("")
    id_number = ObjectProperty("")
    gender = ObjectProperty("")
    date_of_birth = ObjectProperty("")
    created_at = ObjectProperty("")
    next_of_kin = ObjectProperty("")
    level = ObjectProperty("")
    is_deleted = ObjectProperty("")
    is_active = ObjectProperty("")
    number_of_passed_subjects = ObjectProperty("")

    def get_student_details_by_id(self, *args, **kwargs):
        # Fetch student details by ID from the server
        response = StudentsRoutes(
            client=self.manager.connection_client
        ).get_student_by_id(
            student_id=self.manager.get_shared_data("current_student_id"),
        )
        self.first_name = f'{response.json().get("first_name")}'
        self.last_name = f'{response.json().get("last_name")}'
        self.email = f'{response.json().get("email")}'
        self.role = f'{response.json().get("role")}'
        self.phone_number = f'{response.json().get("phone_number")}'
        self.id_number = f'{response.json().get("id_number")}'
        self.gender = f'{response.json().get("gender")}'
        self.date_of_birth = f'{response.json().get("date_of_birth")}'
        self.created_at = f'{response.json().get("created_at")}'
        self.next_of_kin = f'{response.json().get("next_of_kin")}'
        self.level = f'{response.json().get("level")}'
        self.is_deleted = f'{response.json().get("is_deleted")}'
        self.is_active = f'{response.json().get("is_active")}'
        self.number_of_passed_subjects = (
            f'{response.json().get("number_of_passed_subjects")}'
        )

    def on_enter(self):
        # Fetch student details when entering the screen
        self.get_student_details_by_id()

    def deactivate_reactivate(self):
        # Activate or deactivate the student based on current state
        response = CoreRoutes(
            client=self.manager.connection_client
        ).post_activate_deactivate_user(
            student_id=self.manager.current_student_id,
        )
