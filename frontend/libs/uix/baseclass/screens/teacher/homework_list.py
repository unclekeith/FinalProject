import json
import os

from kivy.clock import Clock
from kivy.metrics import dp
from kivy.properties import ObjectProperty
from kivymd.uix.badge import MDBadge
from kivymd.uix.label import MDLabel
from kivymd.uix.list import (
    MDListItem,
    MDListItemHeadlineText,
    MDListItemLeadingIcon,
    MDListItemSupportingText,
)
from kivymd.uix.screen import MDScreen
from libs.applibs.generated_connection_manager import (
    TeachersRoutes,  # Importing TeachersRoutes
)


class HomeworkListScreen(MDScreen):
    first_name = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.documents = []
        self.current_open_document_id = (
            None  # Track the ID of the currently opened document
        )
        self.badge_states = {}  # Track the read/unread status of messages
        self.load_badge_states()  # Load previous badge states from file

    def on_pre_enter(self):
        """Schedule messages retrieval every 5 seconds."""
        self._file_interval = Clock.schedule_interval(self.get_all_documents, 5)

    def on_enter(self):
        """Populate documents when the screen is entered."""
        self.get_all_documents()  # Fetch documents immediately on screen enter

    def get_all_documents(self, dt=None):
        """Fetch all documents from the server."""
        try:
            # Call the API to fetch the document list
            response = TeachersRoutes(
                client=self.manager.connection_client
            ).list_files_teacher_list__get()

            # Ensure a successful HTTP response
            if response.status_code != 200:
                print(f"Error: Server returned status code {response.status_code}")
                self.show_error_message(
                    "Failed to retrieve documents. Please try again later."
                )
                return

            # Parse the JSON response
            all_documents = response.json()

            # Ensure the response contains a valid 'files' list
            if isinstance(all_documents, dict) and "files" in all_documents:
                self.documents = all_documents["files"]
                self.populate_all_documents()
            else:
                print("Unexpected response format:", all_documents)
                self.show_error_message("No valid documents available.")
        except Exception as e:
            print(f"Error fetching documents: {e}")
            self.show_error_message(
                "Error retrieving documents. Please check your connection."
            )

    def populate_all_documents(self):
        """Populate the MDList with the fetched documents."""
        self.ids.posts.clear_widgets()
        self.user = self.manager.get_shared_data("user")

        if self.user:
            try:
                self.first_name = self.user.get("first_name", "")
            except Exception as e:
                print(f"Error updating user data: {e}")
        else:
            print("No user data found.")

        if not self.documents:
            # No documents received
            self.ids.posts.add_widget(
                MDLabel(
                    text="No Document received yet",
                    bold=True,
                    halign="center",
                    padding=(dp(0), dp(200), 0, 0),
                )
            )
        else:
            # Display each document in the list
            for file in self.documents:
                document_name = str(file.get("filename", "Unknown Document"))
                document_id = file.get("id", "unknown_id")

                # Badge logic: Show badge if the document is unread
                badge_text = "" if self.badge_states.get(document_id) == "read" else "1"

                # Define on-click behavior for the list item
                def on_document_click(instance, file=file):
                    self.check_and_download(file["filename"])  # Check and download
                    self.current_open_document_id = file.get("id")
                    self.badge_states[file.get("id")] = "read"  # Mark as read
                    self.save_badge_states()
                    self.populate_all_documents()  # Refresh the list

                # Create a list item
                list_item = MDListItem(
                    MDListItemLeadingIcon(
                        icon="file-document",  # Icon for documents
                    ),
                    MDListItemHeadlineText(
                        text=f"From: {self.first_name}",  # Example text
                    ),
                    MDListItemSupportingText(
                        id=f"supporting_{document_id}",
                        text=document_name,
                    ),
                    MDBadge(text=badge_text),  # Badge for unread documents
                    on_release=on_document_click,
                    id=f"item_{document_id}",
                    md_bg_color=(0, 0, 0, 0),  # Transparent background
                )

                # Add the list item to the MDList
                self.ids.posts.add_widget(list_item)

    def download_file_teacher_download__filename__get(self, filename, **kwargs):
        """Download the file from the server."""
        try:
            response = TeachersRoutes(
                client=self.manager.connection_client
            ).download_file_teacher_download__filename__get(filename, **kwargs)
            return response
        except Exception as e:
            print(f"Error downloading file: {e}")
            return None

    def check_and_download(self, filename):
        """Check if the file exists on the server and download it."""
        response = self.download_file_teacher_download__filename__get(filename)
        if response and response.status_code == 200:
            # Save the file locally
            download_dir = "downloads"
            os.makedirs(download_dir, exist_ok=True)
            file_path = os.path.join(download_dir, filename)
            with open(file_path, "wb") as f:
                f.write(response.content)
            print(f"File downloaded successfully: {file_path}")
        else:
            print(f"File not found on the server: {filename}")

    def show_error_message(self, message):
        """Display an error message in the MDList."""
        self.ids.posts.clear_widgets()
        self.ids.posts.add_widget(
            MDLabel(
                text=message,
                halign="center",
                padding=(dp(0), dp(200), 0, 0),
            )
        )

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
