from kivy.logger import Logger
from kivy.metrics import dp
from kivymd.app import MDApp  # noqa: F401
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen


class StudentChatScreen(MDScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.messages = []
        self.current_open_message_id = (
            None  # Track the ID of the currently opened message
        )

    def on_enter(self):
        self.update_ui(message=self.manager.current_message.get("message"))

    def update_ui(self, message: str = "No Messages"):
        chat_bubble = MDCard(
            MDLabel(text=message, adaptive_height=True),
            style="elevated",
            pos_hint={"center_x": 0.5},
            theme_bg_color="Custom",
            md_bg_color=(0, 255, 1, 250),
            padding=[dp(5), dp(8), dp(5), dp(8)],
            size_hint_x=None,
            width=dp(240),
            adaptive_height=True,
            radius=[dp(0), dp(5), dp(5), dp(5)],
        )

        self.ids.message_container.add_widget(chat_bubble)

    def on_leave(self):
        self.ids.message_container.clear_widgets()