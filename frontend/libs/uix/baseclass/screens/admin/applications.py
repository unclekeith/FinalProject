from kivy.clock import Clock
from kivy.clock import _default_time as time
from kivy.properties import ListProperty, StringProperty
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from libs.applibs.generated_connection_manager import ApplicationsRoutes
from libs.uix.baseclass.components.application_view_list import ApplicationViewListItem

from libs.applibs.generated_connection_manager import StudentsubjectsRoutes

from kivymd.uix.label import MDLabel
from kivy.metrics import dp

class ApplicationsScreen(MDScreen):
    applications = ListProperty([])
    all_count_label = StringProperty("All: 0")  # Bind for all label
    pending_count_label = StringProperty("Pending: 0")  # Bind for pending label
    approved_count_label = StringProperty("Approved: 0")  # Bind for approved label
    rejected_count_label = StringProperty("Rejected: 0")  # Bind for rejected label
    sent_count_label = StringProperty("Sent: 0")  # Bind for sent label

    def on_pre_enter(self):
        self.get_all_applications()
        # Clear current displayed list
        self.ids.application_list.clear_widgets()

    def on_enter(self):
        self.show_loading()

        # Only show SENT applications by default on enter
        self.filter_applications("SENT")

        # Print the ID and Name of the user who sent the application
        self.display_sender_ids()

        # Schedule UI update to consume applications
        Clock.schedule_interval(self.update_ui_with_applications, 0)

    def show_loading(self):
        # Implement loading UI (e.g., spinner) if needed
        pass

    def hide_loading(self):
        # Hide loading UI when data is loaded
        pass


    def get_all_applications(self):
        # Fetch applications from the server
        response = ApplicationsRoutes(
            client=self.manager.connection_client
        ).get_applications()

        # Stop the loading animation when response is received
        self.hide_loading()

        if response.status_code != 200:
            print("Failed to get Applications")
            return

        applications = response.json()
        self.applications = applications
        # Cache the applications for future filtering
        self.manager.set_shared_data("cached_applications", applications)

        # Update badge counts
        self.update_badges(applications)

    def update_badges(self, applications):
        """Helper function to update the badge counts for applications"""
        total_count = len(applications)
        pending_count = sum(1 for app in applications if app.get("status") == "PENDING")
        approved_count = sum(
            1 for app in applications if app.get("status") == "APPROVED"
        )
        rejected_count = sum(
            1 for app in applications if app.get("status") == "REJECTED"
        )
        sent_count = sum(1 for app in applications if app.get("status") == "SENT")

        # Update the label text for each category
        self.all_count_label = f"All: {total_count}"
        self.pending_count_label = f"Pending: {pending_count}"
        self.approved_count_label = f"Approved: {approved_count}"
        self.rejected_count_label = f"Rejected: {rejected_count}"
        self.sent_count_label = f"Sent: {sent_count}"

        # Update badge numbers in UI if needed
        self.ids.pending_badge.badge_text = str(pending_count)
        self.ids.approved_badge.badge_text = str(approved_count)
        self.ids.rejected_badge.badge_text = str(rejected_count)

    def update_ui_with_applications(self, *args) -> None:
        # Limit the update to 60 FPS to avoid blocking the UI
        limit = Clock.get_time() + 1 / 60
        while self.applications and time() < limit:
            application = self.applications.pop(0)
            self.add_application_item(application)
            

    def add_application_item(self, application):
        """Helper function to add an application item to the UI"""
        status = application.get("status")
        applicant_name = application.get("applicant", {}).get("first_name", "Unknown")
        applicant_id = application.get("applicant", {}).get("id", "N/A")

        if status == "APPROVED":
            status_color = "green"
        elif status == "REJECTED":
            status_color = "red"
        elif status == "PENDING":
            status_color = "orange"
        else:
            status_color = "grey"

        # Add the application item to the UI
        application_item = ApplicationViewListItem(
            applicant_name=applicant_name,
            status=status,
            background_color=status_color,
            application=application,
        )

        self.ids.application_list.add_widget(application_item)

    def filter_applications(self, status: str = None) -> None:
        # Reset the applications list to the cached version
        cached_applications = self.manager.get_shared_data("cached_applications")

        if not cached_applications:
            print("No cached applications available")
            return

        # Clear current displayed list
        self.ids.application_list.clear_widgets()

        # If no status is provided, display all cached applications
        if not status:
            filtered_applications = cached_applications
        else:
            # Filter applications by status
            filtered_applications = [
                application
                for application in cached_applications
                if application.get("status") == status
            ]

        # Display "No applications" message if the list is empty
        if not filtered_applications:
            no_applications_label = MDLabel(
                text=f"[color=#08080][b]No applications  {status if status else 'All'}[/b][/color]",
                halign="center",
                size_hint=(None, None),  # Disable automatic sizing
                size=(200, 50),  # Set specific size for better centering
                pos_hint={"center_x": 0.5, "center_y": 0.5},  # Center in the screen
                markup=True,
                theme_text_color="Hint",
            )
            self.ids.application_list.add_widget(no_applications_label)
        else:
            # Set the applications to the filtered list
            self.applications = filtered_applications
            # Schedule UI update to display the filtered applications
            Clock.schedule_interval(self.update_ui_with_applications, 0)

        # Update the badge counts based on the filter applied
        self.update_badges(cached_applications)

    def load_application_details(self, application: dict) -> None:
        # Set the current application details in shared data
        self.manager.set_shared_data("current_application", application)
        # Navigate to the application details screen
        self.manager.push("application_details")

    def display_sender_ids(self):
        """Print the ID and Name of the person who sent the application and fetch subjects."""
        for application in self.applications:
            sender_name = application.get("applicant", {}).get("first_name", "Unknown")
            sender_id = application.get("applicant", {}).get("id", "N/A")
            
            if sender_id:
                # Store the sender_id (which will be used as student_id) in shared data
                self.manager.set_shared_data("student_id", sender_id)
                print(f"Application sent by: {sender_name} (ID: {sender_id})")
                
                # Now fetch and store the subjects associated with this student
                self.get_student_subjects(sender_id)

    def get_student_subjects(self, student_id):
        """Fetch and store the subjects associated with the given student_id."""
        try:
            # Fetch the subjects for the given student_id
            response = StudentsubjectsRoutes(
                client=self.manager.connection_client
            ).get_student_subjects

            # Check if the request was successful
            if response.status_code == 200:
                student_subjects = response.json()

                # Store the subjects in shared data for later use
                self.manager.set_shared_data("student_subjects", student_subjects)
                print(f"Subjects for student {student_id} have been fetched and stored.")
            else:
                print(f"Error fetching subjects for student {student_id}: {response.status_code}")
                
        except Exception as e:
            print(f"Error fetching subjects: {e}")
