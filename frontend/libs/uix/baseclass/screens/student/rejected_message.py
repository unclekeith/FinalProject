from kivymd.uix.screen import MDScreen
from kivy.clock import Clock
from libs.applibs.generated_connection_manager import AuthRoutes
from libs.applibs.generated_connection_manager import CoreRoutes, StudentsRoutes




class MyScreen(MDScreen):
    def on_enter(self):
        Clock.schedule_once(self.switch_screen, 5)
        
    def deactivate_reactivate(self):
        CoreRoutes(client=self.manager.connection_client).post_activate_deactivate_user(
            student_id=self.manager.current_student_id,
        )
        
    def log_out(self):
        AuthRoutes(client=self.manager.connection_client).post_logout()
        self.manager.push_replacement("login")
        
    def switch_screen(self, dt=None):
        self.manager.push_replacement("login")
        self.deactivate_reactivate()
        self.log_out()