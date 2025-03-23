import os
from datetime import datetime
from kivy.logger import Logger  # For debugging
from kivy.uix.image import Image
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.metrics import dp
from libs.applibs.generated_connection_manager import StudentsRoutes  # Import the StudentsRoutes class
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.button import MDButton, MDButtonIcon, MDButtonText, MDIconButton
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarSupportingText

class CameraScreen(MDScreen):

    def capture(self):
        try:
            # Capture and save the image
            capture_time = datetime.now()
            image_path = f"data/images/{capture_time.year}_{capture_time.month}_{capture_time.day}_{capture_time.hour}{capture_time.minute}{capture_time.second}.png"
            os.makedirs(os.path.dirname(image_path), exist_ok=True)  # Ensure the directory exists

            # Capture image from the camera widget
            camera = self.ids.camera_widget
            camera.export_to_png(image_path)

            Logger.info(f"Image saved at {image_path}")
            self.preview_image(image_path)
            self.upload_to_server()

        except Exception as e:
            Logger.error(f"Error capturing image: {e}")

    def preview_image(self, image_path):
        """Preview the captured image and give options to keep or discard it."""
        # Clear any previous widgets in the container
        try:
            self.ids.image_preview_container.clear_widgets()

            # Create the main layout to hold the preview
            main_box = MDBoxLayout(
                orientation="vertical",
                pos_hint={'center_x': 0.5, 'center_y': 0.5},
                size_hint=(None, None),
                size=(dp(300), dp(350)),
                spacing=dp(10),
                padding=dp(10),
            )

            # Add the captured image as preview
            image_widget = Image(source=image_path, size_hint=(None, None), size=(dp(290), dp(340)))
            main_box.add_widget(image_widget)

            # Add buttons to confirm or retake
            button_layout = MDBoxLayout(
                orientation="horizontal", size_hint_y=None, height=dp(50), spacing=dp(10)
            )

            # "Keep" button to confirm the photo
            keep_button = MDButton(
                        MDButtonText(text="Keep Image"),
                        size_hint=(None, None),
                        size=(dp(130), dp(40)),
                        radius=(dp(5)),
            )
            keep_button.bind(on_release=lambda x: self.upload_to_server(image_path))  # Upload after confirmation
            button_layout.add_widget(keep_button)

            # "Retake" button to allow taking another picture
            retake_button = MDButton(
                        MDButtonText(text="Retake"),
                        size_hint=(None, None),
                        size=(dp(130), dp(40)),
                        radius=(dp(5)),
            )
            retake_button.bind(on_release=self.retake_image)  # Retake the photo
            button_layout.add_widget(retake_button)

            # Add the buttons layout to the main box
            main_box.add_widget(button_layout)

            # Add the preview layout to the container
            self.ids.image_preview_container.add_widget(main_box)
        except Exception as e:
            pass
        
    def retake_image(self, instance):
        """Clear the preview and retake the image."""
        self.ids.image_preview_container.clear_widgets()  # Clear the preview
        self.capture()  # Call capture method to retake the image

    def upload_to_server(self, image_path):
        try:
            # Instantiate the StudentsRoutes class
            students_routes = StudentsRoutes(client=self.manager.connection_client)

            with open(image_path, "rb") as image_file:
                # Prepare the multipart/form-data payload
                files = {"file": (os.path.basename(image_path), image_file, "image/png")}
                # Call the upload_profile_picture_student_upload__post function
                response = students_routes.upload_profile_picture_student_upload__post(files=files)

                if response.status_code == 200:
                    Logger.info(f"Image uploaded successfully: {response.json()}")
                    self.succesfully_saved()
                    # self.manager.push("student_dashboard")
                    

                    
                else:
                    Logger.error(f"Failed to upload image: {response.status_code}, {response.text}")
                    MDSnackbar(
                        text="Failed to upload image. Please try again.",
                        y=dp(24),
                        pos_hint={"center_x": 0.5},
                        size_hint_x=0.9,
                    ).open()
        except Exception as e:
            pass
            # Logger.error(f"Error uploading image: {e}")
            # MDSnackbar(
            #     text="Error uploading image. Please try again.",
            #     y=dp(24),
            #     pos_hint={"center_x": 0.5},
            #     size_hint_x=0.9,
            # ).open()



    def succesfully_saved(self):
        MDSnackbar(
            MDSnackbarSupportingText(
                text=" Picture saved successfully!",
            ),
            y=dp(24),
            orientation="vertical",
            pos_hint={"center_x": 0.5},
            size_hint_x=0.9,
            # background_color="white",
        ).open()