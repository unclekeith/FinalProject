from kivy.clock import Clock
from kivy.clock import _default_time as time
from kivy.properties import ListProperty
from kivymd.uix.screen import MDScreen
from libs.applibs.generated_connection_manager import TeachersRoutes
from libs.uix.baseclass.components.user_view_list import UserViewListItem


class StaffScreen(MDScreen):
    staff = ListProperty([])

    def on_pre_enter(self):
        self.get_all_staff()
        # Clear current displayed list
        self.ids.user_list.clear_widgets()

    def on_enter(self):
        self.show_loading()
        Clock.schedule_interval(self.update_ui_with_staff, 0)

    def show_loading(self):
        # Implement loading UI (e.g., spinner) if needed
        pass

    def hide_loading(self):
        # Hide loading UI when data is loaded
        pass

    def get_all_staff(self):
        # Fetch staff from the server
        response = TeachersRoutes(client=self.manager.connection_client).get_teachers()

        # Stop the loading animation when response is received
        self.hide_loading()

        if response.status_code != 200:
            print("Failed to get staff")
            return

        staff = response.json()
        self.staff = staff
        # Cache the staff for future filtering
        self.manager.set_shared_data("cached_staff", staff)

    def update_ui_with_staff(self, *args) -> None:
        # Limit the update to 60 FPS to avoid blocking the UI
        limit = Clock.get_time() + 1 / 60
        while self.staff and time() < limit:
            staff = self.staff.pop(0)
            self.add_user_item(staff)

    def add_user_item(self, user):
        """Helper function to add a user item to the UI"""

        user_item = UserViewListItem(
            fullname=f"{user.get('first_name')} {user.get('last_name')}",
            email=f"{user.get('email')}",
            phone_number=f"{user.get('phone_number')}",
        )

        # Bind the on_click event to the staff item
        user_item.bind(
            on_release=lambda instance, staff=user: self.load_staff_details(staff)
        )

        # Add the user item to the UI
        self.ids.user_list.add_widget(user_item)

    def load_staff_details(self, staff: dict) -> None:
        # Set the current staff details in shared data
        self.manager.set_shared_data("current_staff", staff)
        self.manager.set_shared_data("current_staff_id", staff.get("id"))
        print(self.manager.get_shared_data("current_staff_id"))
        # Navigate to the staff details screen
        self.manager.push("account_details2")

    def profile(self):
        self.manager.push("profile")
