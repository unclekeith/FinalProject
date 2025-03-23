import json
from kivy.clock import Clock
from kivy.metrics import dp
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.boxlayout import BoxLayout
from kivymd.uix.card import MDCard
from kivy.properties import ObjectProperty
from kivymd.uix.badge import MDBadge
from libs.applibs.generated_connection_manager import TeachersRoutes
from libs.uix.baseclass.components.subject_view_list import SubjectListItem

class Replying_Teachers_MessagesScreen(MDScreen):
    first_name = ObjectProperty("")
    teacher_accounts = []
 
    def on_enter(self):
        # Triggering the fetching process when entering the screen
        self.get_all_messages()

    def get_all_messages(self, dt=None):
        try:
            # Fetch data from the server
            response = TeachersRoutes(
                client=self.manager.connection_client
            ).get_teachers_who_sent_messages_teacher_teachers_who_sent_messages__get()

            # Convert the response to JSON (if it's not already)
            if response.status_code == 200:  # Make sure the response is successful
                all_messages = response.json()

                self.messages = all_messages.get("messages", [])
                print(self.messages)

                # Group the messages by teacher_id and count the number of messages for each teacher
                self.group_and_count_messages()

                # Set shared data
                self.manager.set_shared_data("student_teacher_accounts", all_messages)

                # Populate the UI after processing the grouped messages
                self.populate_teacher_accounts()

        except Exception as e:
            print(f"Error fetching messages: {e}")

    def group_and_count_messages(self):
        """Group messages by teacher_id and count how many messages each teacher has sent."""
        # Create a dictionary to group messages by teacher_id
        grouped_messages = {}
        for message in self.messages:
            teacher_id = message["teacher_id"]
            if teacher_id not in grouped_messages:
                grouped_messages[teacher_id] = []
            grouped_messages[teacher_id].append(message)

        # Add the grouped messages to the class variable
        self.grouped_messages = grouped_messages

    def fetch_teacher_names(self):
        """Fetch and return teacher names for each teacher_id."""
        teacher_ids = {message["teacher_id"] for message in self.messages}
        teacher_names = {}

        # Fetch teacher names for each teacher_id
        for teacher_id in teacher_ids:
            teacher_names[teacher_id] = self.get_teacher_name_by_id(teacher_id)

        # Attach teacher names to each message in the grouped messages
        for teacher_id, messages in self.grouped_messages.items():
            teacher_name = teacher_names.get(teacher_id, str(teacher_id))  # Fallback to teacher_id if name not found
            for message in messages:
                message["teacher_name"] = teacher_name

    def get_teacher_name_by_id(self, teacher_id):
        """Function to fetch teacher name by teacher_id."""
        try:
            # API call to fetch the teacher's name by teacher_id
            response = TeachersRoutes(
                client=self.manager.connection_client
            ).get_teacher_name_by_id(teacher_id)

            if response.status_code == 200:
                return response.json().get("name", str(teacher_id))  # Return teacher name or ID if name is not found
            else:
                return str(teacher_id)  # Use teacher_id as fallback
        except Exception as e:
            print(f"Error fetching teacher name for ID {teacher_id}: {e}")
            return str(teacher_id)  # Fallback to teacher_id if error occurs

    def populate_teacher_accounts(self):
        """Populate the teacher accounts with grouped messages and badges."""
        # Clear any existing teacher accounts
        self.ids.teacher_accounts.clear_widgets()

        # Iterate through each teacher's grouped messages and display them
        for teacher_id, messages in self.grouped_messages.items():
            teacher_name = messages[0].get("teacher_name", str(teacher_id))  # Use teacher name or ID if not found
            message_count = len(messages)  # The number of messages sent by the teacher
            
            # Add a box layout to list messages under the teacher's name
            messages_box = BoxLayout(
                orientation="vertical",
                size_hint_y=None,
                height=dp(100) * len(messages),  # Adjust height based on the number of messages
                padding=[dp(10), dp(10)],
                spacing=dp(5)
            )

            # Add each message under the teacher's name
            for message in messages:
                messages_box.add_widget(
                    SubjectListItem(
                        teacher_account=teacher_name,  # Display teacher name
                        message_content=message.get("content", "N/A"),  # Display message content
                        timestamp=message.get("timestamp", "N/A")  # Display timestamp
                    )
                )

            # Add the card to the teacher accounts section
            self.ids.teacher_accounts.add_widget(messages_box)
