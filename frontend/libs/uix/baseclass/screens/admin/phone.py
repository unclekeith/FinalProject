from kivy.clock import Clock
from kivy.metrics import dp
from kivy.properties import StringProperty
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen


class AdminPhone(MDScreen):
    first_name = StringProperty("")
    call_status_label = None
    call_duration = 0  # in seconds
    call_duration_label = None

    # def on_pre_enter(self):
    #     self.first_name = self.manager.get_shared_data("user").get("first_name")

    def minimize_phone(self):
        # Minimize the Phone screen to a small card at the bottom right
        self.size_hint = (None, None)
        self.size = (dp(200), dp(280))  # Size of the minimized card
        self.pos_hint = {"center_x": 0.75, "center_y": 0.5}  # Position at bottom right

        # Optionally, hide other parts of the Phone screen
        self.ids.card.opacity = 1  # Hide the main card content

    def restore_phone(self):
        self.size_hint = (1, 1)  # Restore to full size
        self.size = (None, None)  # Remove fixed size
        self.pos_hint = {"center_x": 0.5, "center_y": 0.5}  # Center it again
        self.ids.card.opacity = 1  # Show the main card content

    def on_enter(self):
        # Create a label for call status
        self.call_status_label = MDLabel(
            text="Connecting...",
            size_hint=(None, None),
            size=(dp(200), dp(50)),
            pos_hint={"center_y": 0.7, "center_x": 0.5},
            padding=(0, 0, 0, dp(12)),
            halign="center",
        )
        self.add_widget(self.call_status_label)

        # Start the call status timer
        Clock.schedule_once(
            self.start_call_duration, 2
        )  # Start counting after 10 seconds

    def update_call_status(self, dt):
        self.call_status_label.text = "Ringing..."  # Update status to "Ringing"
        # Remove the call status label after a short delay

    def remove_call_status_label(self, dt):
        self.remove_widget(self.call_status_label)  # Remove the call status label

    def start_call_duration(self, dt):
        self.call_duration_label = MDLabel(
            text="00:00",
            size_hint=(None, None),
            size=(dp(200), dp(50)),
            pos_hint={"center_y": 0.7, "center_x": 0.5},
            halign="center",
        )
        self.add_widget(self.call_duration_label)

        # Start the timer to update call duration every second
        Clock.schedule_once(self.remove_call_status_label, 1)  # Remove after 1 second
        Clock.schedule_interval(self.update_call_duration, 1)

    def update_call_duration(self, dt):
        self.call_duration += 1
        minutes, seconds = divmod(self.call_duration, 60)
        self.call_duration_label.text = f"{minutes:02}:{seconds:02}"  # Format as MM:SS

    def ended(self):
        self.remove_widget(self.call_duration_label)
        self.call_status_label = MDLabel(
            text="Call ended!",
            size_hint=(None, None),
            size=(dp(200), dp(50)),
            pos_hint={"center_y": 0.7, "center_x": 0.5},
            padding=(0, 0, 0, dp(12)),
            halign="center",
        )
        self.add_widget(self.call_status_label)
        Clock.schedule_once(self.switch_to_next_screen, 3)

    def switch_to_next_screen(self, dt=None):
        self.manager.push("admin_dashboard")
