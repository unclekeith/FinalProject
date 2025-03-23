from kivymd.uix.screen import MDScreen
from libs.applibs.generated_connection_manager import AuthRoutes


class TeacherScreen(MDScreen):
    def log_out(self):
        AuthRoutes(client=self.manager.connection_client).post_logout()
        self.manager.push_replacement("login")
