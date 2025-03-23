from kivymd.uix.screen import MDScreen
from libs.applibs.generated_connection_manager import AuthRoutes


class RegisterScreen(MDScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def register_user(
        self,
        first_name: str,
        last_name: str,
        email: str,
        password: str,
        phone_number: int,
    ):
        register_form = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone_number": phone_number,
            "password": password,
        }
        response = AuthRoutes(client=self.manager.connection_client).post_register(
            data=register_form
        )

        self.manager.user_data_variable = response.json()
        # user_role = response.json().get("role")

        # if user_role:
        #     self.manager.push_replacement(f"{user_role}_dashboard".lower())
        self.manager.push_replacement("login")
