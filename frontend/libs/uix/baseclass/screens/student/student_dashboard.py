from kivy.metrics import dp
from kivy.properties import StringProperty
from kivymd.uix.screen import MDScreen
from libs.applibs.generated_connection_manager import AuthRoutes


class StudentDashboardScreen(MDScreen):
    first_name = StringProperty("")
    last_name = StringProperty("")
    

    # Initialize flags with default values
   
    def on_pre_enter(self, *args):
        # Set the first name from shared data
        self.first_name = self.manager.get_shared_data("user").get("first_name")
        self.last_name = self.manager.get_shared_data("user").get("last_name")
        

    def log_out(self):
        AuthRoutes(client=self.manager.connection_client).post_logout()
        self.manager.push_replacement("login")