import os
from datetime import datetime

from kivy.core.window import Window
from kivy.metrics import dp
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.screen import MDScreen
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText


class CameraScreen(MDScreen):
    def capture(self):
        capture_time = datetime.now()
        self.ids.zbarcam.export_to_png(
            f"data/images/{capture_time.year}_{capture_time.month}_{capture_time.day}_{capture_time.hour}{capture_time.minute}{capture_time.second}.png"
        )