from kivy.animation import Animation
from kivymd.uix.screen import MDScreen
from libs.applibs.generated_connection_manager import AuthRoutes, CoreRoutes


class LoginScreen(MDScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.access_token = ""

    def on_enter(self):
        # Check if the user can be logged in from the current cookie.
        self.response = CoreRoutes(client=self.manager.connection_client).get_me()

        if self.response.status_code == 200:
            user = self.response.json()
            user_role = user.get("role")

            # Share data among screens
            self.manager.set_shared_data("user", user)

            # Check if the user is active or not
            if user_role:
                if user.get("is_active"):
                    self.manager.push_replacement(f"{user_role}_dashboard".lower())
                else:
                    self.manager.push_replacement("inactive")
        elif self.response.status_code == 401:
            # If user is unauthorized, do not proceed to authorized routes
            self.ids.error_label.text = "Unauthorized. Please log in."

    def logout_user(self):
        # Clear session or token
        self.access_token = ""
        # Log out from the server
        AuthRoutes(client=self.manager.connection_client).post_logout()

        # Redirect to login or unauthorized route
        self.manager.push_replacement("login")

    def login_user(self, **kwargs):
        auth_form = {
            "username": kwargs.get("username"),
            "password": kwargs.get("password"),
        }
        self.response = AuthRoutes(client=self.manager.connection_client).post_login(
            data=auth_form
        )

        if self.response.status_code == 200:
            user = self.response.json()
            user_role = user.get("role")

            # Share data among screens
            self.manager.set_shared_data("user", user)

            # Check if the user is active or not
            if user_role:
                if user.get("is_active"):
                    self.manager.push_replacement(f"{user_role}_dashboard".lower())
                else:
                    self.manager.push_replacement("inactive")
        elif self.response.status_code == 401:
            self.animate()
            self.display_error(self.response)
            self.ids.password.text = ""

    def display_error(self, response):
        error_detail = response.json().get("detail", "An error occurred.")
        self.ids.error_label.text = error_detail

    def animate(self, *args, **kwargs):
        self.animation = (
            Animation(font_size=20, duration=0.2)
            + Animation(font_size=24, duration=0.2)
            + Animation(font_size=20, duration=0.2)
        )
        self.animation.repeat = True  # Make the animation loop indefinitely
        self.animation.start(self.ids.error_label)
