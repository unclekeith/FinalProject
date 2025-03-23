from kivy.metrics import dp
from kivy.properties import StringProperty
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.screen import MDScreen
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarSupportingText
from libs.applibs.generated_connection_manager import TeachersRoutes


class ProfileUpdateScreen(MDScreen):
    # Define ObjectProperties for easier access to the widgets
    teaching_subject = StringProperty()
    teacher_id_number = StringProperty()
    teacher_gender = StringProperty()
    teacher_current_academic_level = StringProperty()
    teacher_next_of_kin = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        symbols = ["DIPLOMA", "DEGREE", "MASTERS", "PHD"]
        level_items = [
            {
                "text": symbol,
                "on_release": lambda x=symbol: self.level_set_items(x),
            }
            for symbol in symbols
        ]
        self.level_menu = MDDropdownMenu(
            caller=self.ids.level,
            items=level_items,
            position="bottom",
        ) 

        # Define gender options
        genders = ["MALE", "FEMALE", "OTHER"]
        gender_items = [
            {
                "text": gender,
                "on_release": lambda x=gender: self.gender_set_items(x),
            }
            for gender in genders
        ]
        self.gender_menu = MDDropdownMenu(
            caller=None,  # Caller will be set dynamically
            items=gender_items,
            position="bottom",
            width_mult=4,
        )

    def on_gender_focus(self, instance, value):
        """Handles focus event for the gender field."""
        if value:  # When the field gains focus
            self.gender_menu.caller = instance  # Set the caller to the gender text field
            self.gender_menu.open()
            
    def on_level_focus(self, instance, value):
        """Handles focus event for the gender field."""
        if value:  # When the field gains focus
            self.level_menu.caller = instance  # Set the caller to the gender text field
            self.level_menu.open()

    def on_enter(self, *args):
        # Get user ID from shared data
        user_data = self.manager.get_shared_data("user")
        if user_data:
            self.user_id = user_data.get("id")
            print(f"User ID: {self.user_id}") if self.user_id else print(
                "User ID not found."
            )
        else:
            print("No user data found in shared data.")

    def updates_user(
        self,
        teaching_subject,
        teacher_id_number,
        teacher_gender,
        teacher_current_academic_level,
        teacher_next_of_kin,
    ):
        # Ensure all fields have values
        if not all(
            [
                teaching_subject,
                teacher_id_number,
                teacher_gender,
                teacher_current_academic_level,
                teacher_next_of_kin,
            ]
        ):
            # Display snackbar with the error message
            self.show_snackbar("All fields must be filled out.")
            return

        # Prepare API data
        teacher_update_form = {
            "teaching_subject": teaching_subject,
            "teacher_id_number": teacher_id_number,
            "teacher_gender": teacher_gender,
            "teacher_current_academic_level": teacher_current_academic_level,
            "teacher_next_of_kin": teacher_next_of_kin,
        }

        try:
            response = TeachersRoutes(
                client=self.manager.connection_client
            ).patch_update_teacher(
                teacher_id=self.user_id,
                json=teacher_update_form,
            )

            if response.status_code == 200:
                updated_user_data = response.json()
                self.update_success()
                print("User profile updated successfully.")

                # Update shared user data
                self.manager.set_shared_data("user", updated_user_data)

                # Navigate back to the dashboard
                self.manager.push_replacement("teacher_dashboard")
            else:
                self.show_snackbar(
                    f"Failed to update profile. (Status: {response.status_code})"
                )
        except Exception as e:
            print(f"Error updating profile: {e}")
            self.show_snackbar("An error occurred while updating the profile.")

    def show_snackbar(self, message):
        """Display a snackbar with the provided message."""
        MDSnackbar(
            MDSnackbarSupportingText(text=message),
            y=dp(24),
            orientation="horizontal",
            pos_hint={"center_x": 0.5},
            size_hint_x=0.9,
        ).open()
        
    def update_success(self):
        """Display a snackbar with the provided message."""
        MDSnackbar(
            MDSnackbarSupportingText("User profile updated successfully."),
            y=dp(24),
            orientation="horizontal",
            pos_hint={"center_x": 0.5},
            size_hint_x=0.9,
        ).open()

    def gender_set_items(self, text_item):
        self.ids.Gender.text = text_item  # Correctly set the selected gender
        self.gender_menu.dismiss()


    def level_set_items(self, text_item):
        self.ids.level.text = text_item
        self.level_menu.dismiss()