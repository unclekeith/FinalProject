import os
from kivy.animation import Animation
from kivy.properties import ObjectProperty
from kivymd.uix.screen import MDScreen
from libs.applibs.generated_connection_manager import StudentsRoutes


class StudentId(MDScreen):
    first_name = ObjectProperty()
    last_name = ObjectProperty()
    gender = ObjectProperty()
    date_of_birth = ObjectProperty()
    profile_image = ObjectProperty()  # Reference to the AsyncImage widget in the .kv file
    

    def get_student_details_by_id(self, *agrs, **kwargs):
        response = StudentsRoutes(
            client=self.manager.connection_client
        ).get_student_by_id(
            student_id=self.manager.current_student_id,
        )
        self.first_name = self.manager.get_shared_data("user").get("first_name")
        self.last_name = self.manager.get_shared_data("user").get("last_name")
        self.gender = self.manager.get_shared_data("user").get("gender")
        self.date_of_birth = self.manager.get_shared_data("user").get("date_of_birth")

    def on_pre_enter(self):
        self.get_students_event = self.get_student_details_by_id()
        

    def on_enter(self):
        self.animate_offline()
        self.get_profile_picture()
        self.download_and_display_profile_picture()
        

    def on_leave(self):
        if self.get_students_event:
            self.get_students_event.cancel()

    def animate_offline(self, *args, **kwargs):
        # self.animation.stop(self.ids.status_label)  # Stop any existing animation

        self.animation = (
            Animation(font_size=20, duration=0.2)
            + Animation(font_size=24, duration=0.2)
            + Animation(font_size=20, duration=0.2)
        )
        self.animation.repeat = True  # Make the animation loop indefinitely

        self.animation.start(self.ids.status_label)
        self.ids.status_label.text_color = "#FF0000"
        self.ids.status_label.text = "Print out your student_id"

  
 
    
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
