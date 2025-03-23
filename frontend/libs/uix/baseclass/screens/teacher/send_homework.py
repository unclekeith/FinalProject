import os

from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.image import Image
from kivy.uix.video import Video
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
from libs.applibs.generated_connection_manager import (
    TeachersRoutes,  # Importing TeachersRoutes
)


class SendHomework(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        Window.bind(on_keyboard=self.events)
        self.manager_open = False
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,
            preview=False,  # Show all files
        )
        self.selected_file = None  # To store the selected file path

    def file_manager_open(self):
        """Open the file manager."""
        self.file_manager.show(os.path.expanduser("~"))
        self.manager_open = True

    def select_path(self, path: str):
        """Handle file selection.

        :param path: Path to the selected file.
        """
        self.exit_manager()

        # Clear previous content in the container
        self.ids.image_container.clear_widgets()

        # Main container
        main_box = MDBoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=dp(10),
            size_hint_y=None,
            height=dp(180),
        )

        # Sub-container for preview and details
        preview_box = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(10),
            size_hint_y=None,
            height=dp(150),
        )

        file_extension = os.path.splitext(path)[-1].lower()
        file_name = os.path.basename(path)

        # Determine preview
        if file_extension in [".png", ".jpg", ".jpeg", ".gif", ".bmp"]:
            # Add an image preview
            preview_box.add_widget(
                Image(source=path, size_hint=(None, None), size=(dp(150), dp(150)))
            )
        elif file_extension in [".mp4", ".avi", ".mkv"]:
            # Add a video preview
            preview_box.add_widget(
                Video(source=path, size_hint=(None, None), size=(dp(150), dp(150)))
            )
        else:
            # Add a file icon for unsupported previews
            preview_box.add_widget(
                MDIconButton(
                    icon="file", size_hint=(None, None), size=(dp(150), dp(150))
                )
            )

        # Add file name as a label
        preview_box.add_widget(
            MDLabel(text=file_name, halign="center", valign="middle")
        )

        # Add preview box to main box
        main_box.add_widget(preview_box)

        # Add the main box to the image container
        self.ids.image_container.add_widget(main_box)

        # Show a Snackbar with the file path

        # Save the selected file path
        self.selected_file = path

    def exit_manager(self, *args):
        """Close the file manager."""
        self.manager_open = False
        self.file_manager.close()

    def events(self, instance, keyboard, keycode, text, modifiers):
        """Handle back button presses on Android."""
        if keyboard in (1001, 27):
            if self.manager_open:
                self.file_manager.back()
        return True

    def send_file(self):
        """Send the selected file to the server using TeachersRoutes."""
        if not self.selected_file:
            MDSnackbar(
                MDSnackbarText(
                    text="No file selected.",
                ),
                y=dp(24),
                pos_hint={"center_x": 0.5},
                size_hint_x=0.8,
            ).open()
            return

        # Use TeachersRoutes to upload the file

        with open(self.selected_file, "rb") as file:
            data = {
                "file": (
                    os.path.basename(self.selected_file),
                    file,
                    "application/octet-stream",
                ),
            }

            # Call the method from TeachersRoutes to upload the file
            response = TeachersRoutes(
                client=self.manager.connection_client
            ).upload_file_teacher_upload__post(files=data)

            if response.status_code == 200:
                MDSnackbar(
                    MDSnackbarText(
                        text="File uploaded successfully.",
                    ),
                    y=dp(24),
                    pos_hint={"center_x": 0.5},
                    size_hint_x=0.8,
                ).open()
            else:
                MDSnackbar(
                    MDSnackbarText(
                        text="Failed to upload file.",
                    ),
                    y=dp(24),
                    pos_hint={"center_x": 0.5},
                    size_hint_x=0.8,
                ).open()
        Clock.schedule_once(self.switch_to_next_screen, 4)

    def switch_to_next_screen(self, dt=None):
        self.manager.push("teachers_homework_list")
