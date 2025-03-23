from kivy.metrics import dp
from kivy.properties import StringProperty
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.screen import MDScreen
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarSupportingText
from libs.applibs.generated_connection_manager import StudentsRoutes

class ProfileUpdateScreen(MDScreen):
    # Define ObjectProperties for easier access to the widgets
    id_number = StringProperty()
    date_of_birth = StringProperty()
    number_of_passed_subjects = StringProperty()
    gender = StringProperty()
    previous_school = StringProperty()
    next_of_kin = StringProperty()
    current_academic_level = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        symbols = ["O_LEVEL", "A_LEVEL"]
        level_items = [
            {
                "text": symbol,
                "on_release": lambda x=symbol: self.level_set_item(x),
            }
            for symbol in symbols
        ]
        self.level_menu = MDDropdownMenu(
            caller=self.ids.level,
            items=level_items,
            position="bottom",
        ) 

        genders = ["MALE", "FEMALE", "OTHER"]
        gender_items = [
            {
                "text": gender,
                "on_release": lambda x=gender: self.gender_set_item(x),
            }
            for gender in genders
        ]
        self.gender_menu = MDDropdownMenu(
            caller=self.ids.gender,
            items=gender_items,
            position="bottom",
        )

    def on_enter(self, *agrs, **kwargs):
        # Get user ID from shared data
        user_data = self.manager.get_shared_data("user")
        if user_data:
            self.user_id = user_data.get("id")
            if self.user_id:
                print(f"User ID: {self.user_id}")
            else:
                print("User ID not found in shared data.")
        else:
            print("No user data found in shared data.")

    def updates_user(
        self,
        date_of_birth,
        id_number,
        number_of_passed_subjects,
        gender,
        previous_school,
        next_of_kin,
        current_academic_level,
    ):
        # Ensure all fields have values
        if not all(
            [
                date_of_birth,
                id_number,
                number_of_passed_subjects,
                gender,
                previous_school,
                next_of_kin,
                current_academic_level,
            ]
        ):
            # Display snackbar with the error message
            MDSnackbar(
                MDSnackbarSupportingText(text="All fields must be filled out."),
                y=dp(24),
                orientation="vertical",
                pos_hint={"center_x": 0.5},
                size_hint_x=0.9,
            ).open()
            return

        # Update user profile via API
        student_update_form = {
            "student_id": self.user_id,
            "date_of_birth": date_of_birth,
            "id_number": id_number,
            "number_of_passed_subjects": number_of_passed_subjects,
            "gender": gender,
            "previous_school": previous_school,
            "next_of_kin": next_of_kin,
            "current_academic_level": current_academic_level,
        }
        response = StudentsRoutes(
            client=self.manager.connection_client
        ).patch_update_student(
            student_id=self.manager.get_shared_data("user").get("id"),
            json=student_update_form,
        )
        if response.status_code == 200:
            updated_user_data = response.json()
            self.succesfully_sent()
            

            # Update the shared user data
            self.manager.set_shared_data("user", updated_user_data)

            # Navigate back to the student dashboard
            self.manager.push_replacement("student_dashboard")
        else: 
            MDSnackbar(
                MDSnackbarSupportingText(
                    text=f"Failed to update user profile. Status code: {response.status_code}"
                ),
                y=dp(24),
                orientation="vertical",
                pos_hint={"center_x": 0.5},
                size_hint_x=0.9,
            ).open()
            self.manager.push_replacement("student_dashboard")
            return

    def gender_set_item(self, text_item):
        self.ids.gender.text = text_item
        self.gender_menu.dismiss()

    def level_set_item(self, text_item):
        self.ids.level.text = text_item
        self.level_menu.dismiss()
        
    def succesfully_sent(self):
        MDSnackbar(
            MDSnackbarSupportingText(
                text=" Profile updated",
            ),
            y=dp(24),
            orientation="vertical",
            pos_hint={"center_x": 0.5},
            size_hint_x=0.9,
            # background_color="white",
        ).open()
