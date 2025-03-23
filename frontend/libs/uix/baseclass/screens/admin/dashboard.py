# from kivy.uix.accordion import StringProperty
from kivy.metrics import dp
from kivymd.uix.screen import MDScreen
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarSupportingText
from libs.applibs.generated_connection_manager import AuthRoutes


class AdminDashboard(MDScreen):
    def logout(self):
        AuthRoutes(client=self.manager.connection_client).post_logout()
        self.manager.push_replacement("login")

    def dummy_proceed(self):
        MDSnackbar(
            MDSnackbarSupportingText(
                text="This feature is still under construction !",
            ),
            y=dp(24),
            orientation="vertical",
            pos_hint={"center_x": 0.5},
            size_hint_x=0.9,
            # background_color="white",
        ).open()
