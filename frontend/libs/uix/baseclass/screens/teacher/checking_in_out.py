from kivy.clock import Clock
from kivymd.uix.screen import MDScreen
from libs.applibs.generated_connection_manager import TeachersRoutes

class CheckingScreen(MDScreen):
    PROGRESS_INDICATOR_SIZE = ("120dp", "120dp")
    BUTTON_RADIUS = 42
    BUTTON_COLOR = "green"
    ICON_COLOR = "white"
    ICON_SIZE = "28sp"
    STATUS_CHECK_INTERVAL = 2  # Interval to check status updates

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.teacher_id = None
        self.check_event = None  # Store the scheduled Clock event for checking status
        self.status_displayed = False  # Track if status is already displayed


    def on_pre_enter(self):
        # Fetch the teacher's status immediately before entering the screen
        user_data = self.manager.get_shared_data("user")
        if user_data:
            self.teacher_id = user_data.get("id")

        # Initialize the TeachersRoutes with the connection client from the manager
        self.teacher_routes = TeachersRoutes(client=self.manager.connection_client)

        if self.teacher_id:
            response = self.teacher_routes.get_teacher_by_id(self.teacher_id)
            if response.status_code == 200:
                status = response.json().get("status")
                self.update_status_display(status)
            else:
                print(f"Error fetching teacher status: {response.status_code}")

        # Start checking for status updates periodically
        self.check_event = Clock.schedule_interval(
            self.check_for_updates, self.STATUS_CHECK_INTERVAL
        )

    def on_leave(self):
        if self.check_event:
            Clock.unschedule(self.check_event)

    def check_for_updates(self, dt):
        # Ensure we have a valid teacher ID before making requests
        if self.teacher_id:
            response = self.teacher_routes.get_teacher_by_id(self.teacher_id)
            if response.status_code == 200:
                status = response.json().get("status")
                self.update_status_display(status)
            else:
                print(f"Error fetching teacher status: {response.status_code}")

    def update_status_display(self, status):
        # Update the status text and icon based on the response
        if status == "CHECKED_IN":
            self.ids.label1.text = "Checked In"
            self.ids.icon.icon = "check-circle"
            self.ids.icon.theme_text_color = "Custom"
            self.ids.icon.text_color = "green"
        elif status == "PENDING":
            self.ids.label1.text = "Pending"
            self.ids.icon.icon = "progress-clock"
            self.ids.icon.theme_text_color = "Custom"
            self.ids.icon.text_color = "purple"
        elif status == "CHECKED_OUT":
            self.ids.label1.text = "Checked Out"
            self.ids.icon.icon = "close-circle"
            self.ids.icon.theme_text_color = "Custom"
            self.ids.icon.text_color = "red"
        else:
            self.ids.label1.text = "Sent"
            self.ids.icon.icon = "send-circle"
            self.ids.icon.theme_text_color = "Custom"
            self.ids.icon.text_color = "orange"

    def check_in(self):
        # Send a request to check in the teacher
        response = self.teacher_routes.check_in_staff_by_id(self.teacher_id)
        if response.status_code == 200:
            print("Checked in successfully.")
            self.update_status_display("CHECKED_IN")
        else:
            print(f"Check-in failed: {response.status_code}")

    def check_out(self):
        # Send a request to check out the teacher
        response = self.teacher_routes.check_out_staff_by_id(self.teacher_id)
        if response.status_code == 200:
            print("Checked out successfully.")
            self.update_status_display("CHECKED_OUT")
        else:
            print(f"Check-out failed: {response.status_code}")
