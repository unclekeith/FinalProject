import json
import os

from kivy.clock import Clock
from kivy.metrics import dp
from kivymd.uix.badge import MDBadge
from kivymd.uix.label import MDLabel
from kivymd.uix.list import (
    MDListItem,
    MDListItemHeadlineText,
    MDListItemLeadingAvatar,
    MDListItemSupportingText,
)
from kivymd.uix.screen import MDScreen
from libs.applibs.generated_connection_manager import MessagesRoutes


class StudentMessageScreen(MDScreen):
    def __init__(self, **kwargs):
        super(StudentMessageScreen, self).__init__(**kwargs)
        self.messages = []
        self.current_open_message_id = None  # Track the ID of the currently opened message
        self.badge_states = {}  # Track the read/unread status of messages
        self.load_badge_states()  # Load previous badge states from file

    def on_pre_enter(self):
        # Schedule messages retrieval every 5 seconds
        self._message_interval = Clock.schedule_interval(self.get_all_messages, 5)

    def on_enter(self):
        # Populate the list and load badge states
        self.populate_all_messages()

    def get_all_messages(self, dt=None):
        try:
            response = MessagesRoutes(
                client=self.manager.connection_client
            ).get_messages()
            new_messages = response.json()

            if new_messages != self.messages:
                self.messages = new_messages
                self.populate_all_messages()

        except Exception as e:
            print(f"Error fetching messages: {e}")

    def populate_all_messages(self):
        self.ids.posts.clear_widgets()

        if not self.messages:
            self.ids.posts.add_widget(
                MDLabel(
                    text="No messages received yet",
                    bold=True,
                    markup=True,
                    halign="center",
                    padding=(dp(0), dp(200), 0, 0),
                )
            )
        else:
            for message in self.messages:
                sy = f"{message.get('message')}"
                message_id = message.get("id")

                # Determine if the message is read or unread (using badge states)
                badge_text = "" if self.badge_states.get(message_id) == "read" else "1"  # Show badge for unread

                def on_student_click(instance, message=message):
                    # Set current message ID when a message is opened
                    self.current_open_message_id = message.get("id")
                    self.badge_states[message.get("id")] = "read"  # Mark the message as read
                    self.save_badge_states()  # Save the updated badge state
                    self.populate_all_messages()  # Refresh message list
                    self.manager.current_message = message
                    self.manager.push("student_chat")

                # Create the list item for the message
                list_item = MDListItem(
                    MDListItemLeadingAvatar(
                        source="data/images/calender.png",
                    ),
                    MDListItemHeadlineText(
                        text=" Admin",
                    ),
                    MDListItemSupportingText(
                        id=f"supporting_{message_id}",
                        text=f"{sy}",
                    ),
                    MDBadge(text=badge_text),  # Add badge for unread messages
                    on_release=on_student_click,
                    id=f"item_{message_id}",  # Unique ID for identifying list item
                    md_bg_color=(0, 0, 0, 0),  # Transparent background
                )

                self.ids.posts.add_widget(list_item)

    def change_icon(self, dt):
        # Ensure that badge states are updated when leaving the screen
        if self.current_open_message_id:
            self.badge_states[self.current_open_message_id] = "read"
            self.save_badge_states()  # Save the updated badge state to the file

    def on_leave(self):
        # Update badge status when leaving the screen
        self.change_icon(0)
        if hasattr(self, "_message_interval"):
            self._message_interval.cancel()

    def load_badge_states(self):
        """Load the badge (read/unread) states from a file."""
        if os.path.exists("badge_states.json"):
            with open("badge_states.json", "r") as f:
                self.badge_states = json.load(f)
        else:
            self.badge_states = {}

    def save_badge_states(self):
        """Save the badge (read/unread) states to a file."""
        with open("badge_states.json", "w") as f:
            json.dump(self.badge_states, f)
