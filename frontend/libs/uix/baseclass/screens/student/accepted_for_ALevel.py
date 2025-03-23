from kivymd.uix.screen import MDScreen
from kivy.clock import Clock
from libs.applibs.generated_connection_manager import AuthRoutes
from libs.applibs.generated_connection_manager import CoreRoutes, StudentsRoutes




class AcceptedScreen(MDScreen):
    def on_enter(self):
        Clock.schedule_once(self.switch_screen, 10)
        
    def switch_screen(self, dt=None):
        self.manager.push_replacement("student_dashboard")
       