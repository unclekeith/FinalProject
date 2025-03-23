from datetime import datetime

from kivy.clock import Clock
from kivy.logger import Logger
from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarSupportingText
from libs.applibs.generated_connection_manager import MessagesRoutes

    
class AdminChatScreen(MDScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.messages = []  # Store messages here if needed

    def send_message(self, message: str):
        if not message.strip():  # Avoid sending empty messages
            Logger.warning("AdminChatScreen: Attempted to send an empty message.")
            self.show_error()
            return

        response = MessagesRoutes(
            client=self.manager.connection_client
        ).post_send_message(json={"message": message})
        Logger.info(f"Message sent: {message}")

        if response.status_code == 200:
            self.update_ui(message=message, success=True)
            self.ids.message.text = ""
        else:
            Logger.error(f"Failed to send message. Status code: {response.status_code}")
            self.update_ui(message="FAILED TO SEND MESSAGE", success=False)
            self.ids.message.text = ""

    def update_ui(self, message: str, success: bool = True):
        bg_color = (
            (0, 255, 0, 1) if success else (255, 0, 0, 1)
        )  # Green for success, red for failure

        # Create the chat bubble layout
        box_layout = MDBoxLayout(
            MDLabel(text=message, adaptive_height=True),
            MDIconButton(
                id="buttonicon",
                icon="check",
                size_hint=(None, None),
                size=(dp(40), dp(40)),
                pos_hint={"right": 1, "bottom": 0},
                adaptive_height=True,
            ),
            MDLabel(
                text=datetime.now().strftime("%H:%M"),
                adaptive_height=True,
                size_hint=(None, None),
                size=(dp(60), dp(30)),
                pos_hint={"right": 1, "bottom": 0},
            ),
            orientation="horizontal",
            padding=[dp(0), dp(8), dp(5), dp(8)],
            size_hint_x=None,
            width=dp(300),
            adaptive_height=True,
            radius=[dp(0), dp(15), dp(15), dp(15)],
        )

        chat_bubble = MDCard(
            box_layout,
            pos_hint={"center_x": 0.5},
            theme_bg_color="Custom",
            md_bg_color=bg_color,
            padding=[dp(6), dp(8), dp(5), dp(0)],
            size_hint_x=None,
            width=dp(300),
            adaptive_height=True,
            radius=[dp(0), dp(15), dp(15), dp(15)],
        )

        # Add the chat bubble to the container
        self.ids.message_container.add_widget(chat_bubble)
        self.ids.message_container.height += (
            chat_bubble.height
        )  # Adjust container height
        self.ids.message_container.scroll_y = 0  # Scroll to the bottom

        # Schedule icon change after 5 seconds
        Clock.schedule_once(self.change_icon, 2)

    def change_icon(self, dt):
        # Find the icon button in the message container and change its icon
        for widget in self.ids.message_container.children:
            if isinstance(widget, MDCard):
                for sub_widget in widget.children:
                    if isinstance(sub_widget, MDBoxLayout):
                        for inner_widget in sub_widget.children:
                            if isinstance(inner_widget, MDIconButton):
                                inner_widget.icon = "check-all"
                                return

    def show_error(self):
        MDSnackbar(
            MDSnackbarSupportingText(
                text="Cannot send an empty message.",
            ),
            y=dp(24),
            orientation="vertical",
            pos_hint={"center_x": 0.5},
            size_hint_x=0.9,
        ).open()

    def receive_call(self, caller_id):
        # Handle incoming call from a student
        Logger.info(f"Incoming call from {caller_id}.")
        # Here, you could show a dialog or notification to accept the call.
