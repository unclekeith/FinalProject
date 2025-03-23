from kivymd.uix.screen import MDScreen
from libs.applibs.generated_connection_manager import CoreRoutes
from kivy.properties import ObjectProperty
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarSupportingText
from kivy.metrics import dp


class ResetPasswordScreen(MDScreen):
    new_password = ObjectProperty()
        
    def reset(
        self,
        email,
        password
    ):
        # Ensure all fields have values
        if not all(
            [
                email,
                password
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
            "email":email,
            "new_password": password,
            
        }
        response = CoreRoutes(
            client=self.manager.connection_client
        ).patch_reset_password(
            email=self.manager.get_shared_data("user").get("email"),
            json=student_update_form,
        )
        if response.status_code == 200:
            # updated_user_data = response.json()
            print("User profile updated successfully.")

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
            self.manager.push_replacement("login")
            return