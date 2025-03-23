from kivy.clock import Clock
from kivy.properties import StringProperty
from kivymd.uix.screen import MDScreen
from libs.applibs.generated_connection_manager import StudentsRoutes

import os


class ProfileScreen(MDScreen):
    # Define ObjectProperty bindings for profile data
    first_name = StringProperty("change me")
    last_name = StringProperty("change me")
    teaching_subject = StringProperty("Not available")  # Provide default value
    teacher_id_number = StringProperty("Not available")  # Provide default value
    teacher_gender = StringProperty("Not available")  # Provide default value
    teacher_current_academic_level = StringProperty("Not available")  # Provide default value
    teacher_next_of_kin = StringProperty("Not available")  # Provide default value

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.previous_user_data = None  # Store the previous user data

        # Schedule the update check every 2 seconds
        Clock.schedule_once(self.initial_check, 0)  # Initial check when screen is first shown
        Clock.schedule_interval(self.check_for_updates, 2)  # Check for updates every 2 seconds

    def on_leave(self):
        """Called when the screen is left. Unschedule the checks."""
        Clock.unschedule(self.initial_check)  # Unschedule the initial check
        Clock.unschedule(self.check_for_updates)  # Unschedule the periodic updates

    def initial_check(self, dt):
        """Force initial update when screen is first shown."""
        self.update_user_data()
        
    def on_enter(self):
        self.update_user_data()
        Clock.unschedule(self.initial_check)  # Unschedule the initial check
        Clock.unschedule(self.check_for_updates)  # Unschedule the periodic updates
        self.get_profile_picture()
        self.download_and_display_profile_picture()

    def check_for_updates(self, dt):
        """This function is called every 2 seconds to check for user data updates."""
        current_user_data = self.manager.get_shared_data("user")

        # Check if the current user data has changed compared to the previous data
        if current_user_data != self.previous_user_data:
            print("User data has changed, updating profile...")
            self.update_user_data()  # Update the profile with the new data
            self.previous_user_data = current_user_data  # Store the new data as previous for next comparison

    def update_user_data(self):
        """Populate the fields with user data."""
        self.user = self.manager.get_shared_data("user")
        try:

            if self.user:
                self.first_name = self.user.get("first_name", "Not available")
                self.last_name = self.user.get("last_name", "Not available")
                self.teaching_subject = self.user.get("teaching_subject", "Not available")
                self.teacher_id_number = self.user.get("teacher_id_number", "Not available")
                self.teacher_gender = self.user.get("teacher_gender", "Not available")
                self.teacher_current_academic_level = self.user.get("teacher_current_academic_level", "Not available")
                self.teacher_next_of_kin = self.user.get("teacher_next_of_kin", "Not available")
                print("Profile updated with the latest data.")
            else:
                print("No user data found.")
        except Exception as e:
            print("It cant work")

    def get_profile_picture(self):
        """
        Fetches and sets the profile picture for the current user.
        This can be either from a URL or a local path.
        """
        # Get the user data (this assumes you have a user data manager)
        user_data = self.manager.get_shared_data("user")
        
        if user_data:
            user_id = user_data.get("id")  # Get the user ID from the shared data
            print(f"User ID: {user_id}")
        else:
            print("User data not found.")
            return

        # Initialize the StudentsRoutes with the connection client
        student_routes = StudentsRoutes(client=self.manager.connection_client)

        if user_id:
            try:
                # Fetch documents associated with the user_id
                response = student_routes.list_user_documents_student_documents__user_id__get(user_id)

                # Log the full response to check the structure
                print("Response:", response.text)

                if response.status_code != 200:
                    print(f"Failed to fetch documents. Status code: {response.status_code}")
                    return

                # Parse the response JSON to get the documents list
                documents = response.json().get("documents", [])
                if not documents:
                    print("No documents found for the user.")
                    return

                # Log the documents to verify if we have correct data
                print("Documents:", documents)

                # Assuming the first document is the profile picture
                profile_picture = documents[0].get("filepath")  # Extract the file path from the document
                file_id = documents[0].get("id")  # Extract the file_id for the download function
                
                if not profile_picture or not file_id:
                    print("No profile picture or file ID found in documents.")
                    return

                # Log and display the profile picture in the MDCard
                print(f"Profile Picture Path: {profile_picture}")
                self.ids.profile_image.source = profile_picture  # Set the source of the AsyncImage

                # Now call the download function to fetch the image if it exists
                self.download_and_display_profile_picture(user_id, file_id)

            except Exception as e:
                print(f"Error fetching profile picture: {e}")
        else:
            print("User ID not found.")

    def download_and_display_profile_picture(self):
        """
        Downloads the profile picture using the user_id,
        then displays it after downloading.
        """
        # Get the user data (this assumes you have a user data manager)
        user_data = self.manager.get_shared_data("user")
        
        if user_data:
            user_id = user_data.get("id")  # Get the user ID from the shared data
            print(f"User ID: {user_id}")
        else:
            print("User data not found.")
            return

        # Initialize the StudentsRoutes with the connection client
        student_routes = StudentsRoutes(client=self.manager.connection_client)

        try:
            # Call the download function to get the document by user_id
            response = student_routes.download_document_student_documents__user_id__download_get(user_id)

            # Ensure that the response is valid
            if response.status_code != 200:
                print(f"Failed to download the document. Status code: {response.status_code}")
                return

            # Define the directory where to save the image
            save_directory = "/home/uncle_k8ith/Keith/uploads/"
            
            # Ensure the directory exists
            if not os.path.exists(save_directory):
                os.makedirs(save_directory)  # Create the directory if it does not exist

            # Define the file path for saving the image
            file_path = os.path.join(save_directory, "profile_picture.jpg")

            # Save the image locally
            with open(file_path, "wb") as f:
                f.write(response.content)

            # Now, set the saved image file as the source for the profile image widget
            print(f"Profile Picture saved to: {file_path}")
            self.ids.profile_image.source = file_path  # Update the AsyncImage source to the local file

        except Exception as e:
            print(f"Error downloading or displaying profile picture: {e}")
