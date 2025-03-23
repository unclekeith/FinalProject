import os
import requests
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.uix.image import Image
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarSupportingText
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDIconButton
from kivymd.uix.label import MDLabel
from kivy.logger import Logger
from libs.applibs.generated_connection_manager import StudentsubjectsRoutes

class PictureSelectScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.manager_open = False
        self.selected_file = None  # To store the selected file path
        self.student_id = None  # The student ID for fetching the certificate

        # File manager initialization
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,
            preview=False,
        )

        # Bind back button to the file manager
        Window.bind(on_keyboard=self.events)

    def on_enter(self):
        """This method is called when the screen is shown."""
        self.get_certificate()
        user_data = self.manager.get_shared_data("user")
        
        if user_data:
            self.student_id = user_data.get("id")  # Get the user ID from the shared data
        else:
            return

    def get_certificate(self):
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

        # Initialize the StudentsubjectsRoutes with the connection client
        student_routes = StudentsubjectsRoutes(client=self.manager.connection_client)

        if user_id:
            try:
                # Fetch documents associated with the user_id
                response = student_routes.get_uploaded_certificate_student_subject_certificate__student_id__get(user_id)

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
                certificate = documents[0].get("filepath")  # Extract the file path from the document
                file_id = documents[0].get("id")  # Extract the file_id for the download function
                
                if not certificate or not file_id:
                    print("No certificate or file ID found in documents.")
                    return

                # Log and display the profile picture in the MDCard
                print(f"certificate Path: {certificate}")
                self.ids.image_container.source = certificate  # Set the source of the AsyncImage

                 # Ensure the directory exists
                if not os.path.exists(certificate):
                    os.makedirs(certificate)  # Create the directory if it does not exist

                # Define the file path for saving the image
                file_path = os.path.join(certificate, "profile_picture.jpg")

                # Save the image locally
                with open(file_path, "wb") as f:
                    f.write(response.content)

                # Now, set the saved image file as the source for the profile image widget
                print(f"Profile Picture saved to: {file_path}")
                self.ids.image_container.source = file_path  # Update the AsyncImage source to the local file

            except Exception as e:
                print(f"Error downloading or displaying profile picture: {e}")


            except Exception as e:
                print(f"Error fetching certificate: {e}")
        else:
            print("User ID not found.")



    def display_image(self, image_path):
        """Display the image directly from the saved file."""
        self.ids.image_container.clear_widgets()  # Clear any existing widgets

        try:
            if os.path.exists(image_path):  # Ensure the file exists
                Logger.info(f"Image file exists at: {image_path}")
                image_widget = Image(source=image_path, size_hint=(None, None), size=(dp(240), dp(240)))
                self.ids.image_container.add_widget(image_widget)
                Logger.info(f"Image displayed successfully from path: {image_path}")
            else:
                Logger.error(f"Image not found at: {image_path}")
                MDSnackbar(
                    MDSnackbarSupportingText(
                        text="Failed to display image. File not found.",
                    ),
                    y=dp(24),
                    orientation="vertical",
                    pos_hint={"center_x": 0.5},
                    size_hint_x=0.9,
                ).open()
        except Exception as e:
            Logger.error(f"Error loading image: {str(e)}")
            MDSnackbar(
                MDSnackbarSupportingText(
                    text=f"Error loading image: {str(e)}",
                ),
                y=dp(24),
                orientation="vertical",
                pos_hint={"center_x": 0.5},
                size_hint_x=0.9,
            ).open()


    def show_no_image_message(self):
        """Show message if no image has been uploaded yet."""
        MDSnackbar(
            MDSnackbarSupportingText(
                text="Nothing sent yet!",
            ),
            y=dp(24),
            orientation="vertical",
            pos_hint={"center_x": 0.5},
            size_hint_x=0.9,
        ).open()

    def file_manager_open(self):
        """Open the file manager."""
        self.file_manager.show(os.path.expanduser("~"))  # Start at home directory
        self.manager_open = True

    def select_path(self, path):
        """Handle file selection and display it."""
        self.exit_manager()

        # Clear any existing content in the image container
        self.ids.image_container.clear_widgets()

        # Main container (centered vertically and horizontally)
        main_box = MDBoxLayout(
            orientation="vertical",
            pos_hint={'center_x': 0.5, 'center_y': 0.5},  # Center vertically at 0.5
            spacing=dp(10),
            padding=(dp(0), dp(0), dp(0), dp(260)),  # Padding at the bottom
            size_hint=(None, None),  # No scaling to ensure fixed dimensions
            size=(dp(250), dp(300)),  # Explicit size
        )
        file_name = os.path.basename(path)

        # Add file preview (only for images)
        if path.lower().endswith((".png", ".jpg", ".jpeg", ".bmp")):
            image_widget = Image(
                source=path, size_hint=(None, None), size=(dp(240), dp(240))
            )
            main_box.add_widget(image_widget)
        else:
            icon_widget = MDIconButton(
                icon="file", size_hint=(None, None), size=(dp(150), dp(150))
            )
            main_box.add_widget(icon_widget)

        # Add file name as a label
        label_widget = MDLabel(
            text=file_name, 
            halign="center", 
            valign="middle", 
            size_hint_y=None, 
            height=dp(30),
        )
        main_box.add_widget(label_widget)

        # Add the constructed layout to the container
        self.ids.image_container.add_widget(main_box)

        # Enable the "Send" button
        self.ids.send_fab.disabled = False

        # Store the selected file path
        self.selected_file = path

    def exit_manager(self, *args):
        """Close the file manager."""
        self.manager_open = False
        self.file_manager.close()

    def events(self, instance, keyboard, keycode, text, modifiers):
        """Handle back button presses on Android."""
        if keyboard in (1001, 27):  # Back button keycodes
            if self.manager_open:
                self.file_manager.back()
                return True
        return False

    def upload_selected_image(self):
        """Uploads the selected file to the server."""
        if not self.selected_file:
            MDSnackbar(
                MDSnackbarSupportingText(
                    text="No file selected to upload!",
                ),
                y=dp(24),
                orientation="vertical",
                pos_hint={"center_x": 0.5},
                size_hint_x=0.9,
            ).open()
            return

        try:
            students_routes = StudentsubjectsRoutes(client=self.manager.connection_client)
            
            # Read file in binary mode
            with open(self.selected_file, "rb") as file:
                files = {'file': (os.path.basename(self.selected_file), file, 'image/jpeg')}  # Adjust MIME type if needed

                response = students_routes.upload_file_student_subject_upload__post(files=files)

                if response.status_code == 200:
                    Logger.info(f"Image uploaded successfully: {response.json()}")

                    # Directly display the uploaded image without caching
                    self.display_image(self.selected_file)

                    MDSnackbar(
                        MDSnackbarSupportingText(
                            text="File uploaded successfully!",
                        ),
                        y=dp(24),
                        orientation="vertical",
                        pos_hint={"center_x": 0.5},
                        size_hint_x=0.9,
                    ).open()

                    # Clear the widget and reset the state
                    self.clear_widget_state()
                else:
                    MDSnackbar(
                        MDSnackbarSupportingText(
                            text=f"Upload failed: {response.text}",
                        ),
                        y=dp(24),
                        orientation="vertical",
                        pos_hint={"center_x": 0.5},
                        size_hint_x=0.9,
                    ).open()

        except Exception as e:
            MDSnackbar(
                MDSnackbarSupportingText(
                    text=f"Upload failed: {str(e)}",
                ),
                y=dp(24),
                orientation="vertical",
                pos_hint={"center_x": 0.5},
                size_hint_x=0.9,
            ).open()

    def clear_widget_state(self):
        """Clears the selected file and resets the UI."""
        self.selected_file = None
        self.ids.image_container.clear_widgets()
        self.ids.send_fab.disabled = True
