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
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from libs.applibs.generated_connection_manager import TeachersRoutes


class TeacherChatScreen(MDScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.messages = []  # Store messages here if needed
        Window.bind(on_keyboard=self.on_keyboard)

    def send_message(self, message: str):
        if not message.strip():  # Avoid sending empty messages
            Logger.warning("You attempted to send an empty message.")
            self.show_error()
            return

        user_data = self.manager.get_shared_data("user")
        if user_data:
            self.user_id = user_data.get("id")
        
        if not self.user_id:
            Logger.error("TeacherChatScreen: No user ID found.")
            return

        # Send request with teacher_id
        response = TeachersRoutes(
            client=self.manager.connection_client
        ).send_message_teacher_send_message__post(
            params={"teacher_id": self.user_id},  # Include teacher_id
            json={"content": message}  # Change "message" to "content" if required
        )

        Logger.info(f"Message sent: {message}")
        Logger.info(f"API Response: {response.json()}")  # Debug response

        if response.status_code == 200:
            self.update_ui(message=message, success=True)
            self.ids.message.text = ""
        else:
            Logger.error(f"Failed to send message. Status code: {response.status_code}")
            Logger.error(f"Response: {response.text}")  # Log full response
            self.update_ui(message="FAILED TO SEND MESSAGE", success=False)
            self.ids.message.text = ""

    def update_ui(self, message: str, success: bool = True):
        """Update the UI with a new sent message."""
        bg_color = (
            (0, 255, 0, 1) if success else (255, 0, 0, 1)
        )  # Green for success, red for failure

        # Create the chat bubble layout for the sent message
        box_layout = MDBoxLayout(
            MDLabel(text=message, adaptive_height=True),
            # MDIconButton(
            #     id="buttonicon",
            #     icon="check",
            #     size_hint=(None, None),
            #     size=(dp(40), dp(40)),
            #     pos_hint={"right": 1, "bottom": 0},
            #     adaptive_height=True,
            # ),
            orientation="horizontal",
            padding=[dp(0), dp(8), dp(5), dp(8)],
            size_hint_x=None,
            width=dp(300),
            adaptive_height=True,
            radius=[dp(0), dp(15), dp(15), dp(15)],
        )

        chat_bubble = MDCard(
            box_layout,
            pos_hint={"left": 1},  # Position sent messages on the left
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
        """Change the icon after the message is successfully sent."""
        for widget in self.ids.message_container.children:
            if isinstance(widget, MDCard):
                for sub_widget in widget.children:
                    if isinstance(sub_widget, MDBoxLayout):
                        for inner_widget in sub_widget.children:
                            if isinstance(inner_widget, MDIconButton):
                                inner_widget.icon = "check-all"
                                return

    def show_error(self):
        """Display an error message if an empty message is sent."""
        MDSnackbar(
            MDSnackbarSupportingText(text="Cannot send an empty message."),
            y=dp(24),
            orientation="vertical",
            pos_hint={"center_x": 0.5},
            size_hint_x=0.9,
        ).open()

    def pre_enter(self):
        """Fetch replies when the screen is entered."""
        self.fetch_replies()
        
    def on_enter(self):
        Clock.schedule_once(self.fetch_replies, 0)  # Initial check on enter
        # Clock.schedule_interval(self.fetch_replies, 2)  # Check every 2 seconds/

    def on_keyboard(self, instance, key, *args):
        """Listen for Enter key press and trigger message fetch."""
        if key == 40:  # Enter key
            self.fetch_replies()
            return True
        return False

    def fetch_replies(self, *args):
        """Fetch replies from the server and update UI."""
        user_data = self.manager.get_shared_data("user")
        if user_data:
            self.user_id = user_data.get("id")
        
        if not self.user_id:
            Logger.error("TeacherChatScreen: No user ID found.")
            return

        # Fetch replies using GET request with query parameters
        response = TeachersRoutes(client=self.manager.connection_client).get_replies_endpoint_teacher_get_replies__get(
            params={"teacher_id": self.user_id}  # Ensure correct query parameter format
        )

        if response.status_code == 200:
            try:
                data = response.json()
                Logger.info(f"API Response: {data}")  # Debugging API response

                replies = data.get("replies", [])
                if replies:
                    for reply in replies:
                        Logger.info(f"Reply Data: {reply}")  # Log each reply object
                        message_text = reply.get("content", "No message found")  # Use 'content' instead
                        self.update_the_ui(message_text, success=True)  
                else:
                    Logger.warning("No replies found in API response.")
            
            except Exception as e:
                Logger.error(f"Failed to parse API response: {e}")
        else:
            Logger.error(f"Failed to fetch replies. Status code: {response.status_code}")

    def update_the_ui(self, message: str, success: bool = True):
        """Update chat UI with received messages."""
        # Create the chat bubble layout for the received message (position it on the right)
        box_layout = MDBoxLayout(
            MDLabel(text=message, adaptive_height=True),
            orientation="horizontal",
            padding=[dp(0), dp(8), dp(5), dp(8)],
            size_hint_x=None,
            width=dp(300),
            adaptive_height=True,
            radius=[dp(0), dp(15), dp(15), dp(15)],
            pos_hint={"right": 1, "top": 1},  # Align to the right for received messages
        )

        chat_bubble = MDCard(
            box_layout,
            theme_bg_color="Custom",
            md_bg_color="blue",  # Color for received messages
            padding=[dp(6), dp(8), dp(5), dp(0)],
            size_hint_x=None,
            width=dp(300),
            adaptive_height=True,
            radius=[dp(0), dp(15), dp(15), dp(15)],
        )

        # Add the chat bubble to the container
        if "messages_container" in self.ids:
            self.ids.messages_container.add_widget(chat_bubble)
            self.ids.messages_container.height += chat_bubble.height  # Adjust container height
            self.ids.messages_container.scroll_y = 0  # Scroll to the bottom
        else:
            Logger.error("TeacherChatScreen: messages_container not found in ids.")
