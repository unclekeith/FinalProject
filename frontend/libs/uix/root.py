import importlib
import json
from typing import Optional

from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import DictProperty
from kivymd.uix.screenmanager import MDScreenManager
from libs.applibs import utils
from libs.applibs.generated_connection_manager import create_client


class Root(MDScreenManager):
    history = []  # List of tuples (screen_name, side)
    shared_data = DictProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.shared_data = {}
        Window.bind(on_keyboard=self._handle_keyboard)
        self.current_student_id = 0

        try:
            # Create a connection client
            self.connection_client = create_client()
            # Load the screens data
            with open(utils.abs_path("screens.json")) as f:
                self.screens_data = json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            print(f"Error loading screens data: {e}")
            self.screens_data = {}

    def push(self, screen_name: str, side: str = "left") -> None:
        """Appends the screen to the navigation history and sets `screen_name` as the current screen."""
        if self.current != screen_name:
            self.history.append((screen_name, side))

        self.load_screen(screen_name)
        self.transition.direction = side
        self.current = screen_name

    def push_replacement(self, screen_name: str, side: str = "left") -> None:
        """Clears the navigation history and sets the current screen to `screen_name`."""
        self.history.clear()
        self.push(screen_name, side)

    def back(self) -> None:
        """Removes the current screen from the navigation history and sets the current screen to the previous one."""
        if len(self.history) <= 1:
            return

        cur_screen, cur_side = self.history.pop()
        prev_screen, _ = self.history[-1]

        self.transition.direction = {
            "left": "right",
            "right": "left",
            "up": "down",
            "down": "up",
        }.get(cur_side, "left")

        self.current = prev_screen

    def set_shared_data(self, key: str, value: Optional[any]) -> None:
        """Sets a key-value pair in the shared data store."""
        self.shared_data[key] = value

    def get_shared_data(self, key: str) -> Optional[any]:
        """Returns the value associated with `key` in the shared data store."""
        return self.shared_data.get(key, None)

    def _handle_keyboard(self, instance, key: int, *args) -> bool:
        if key == 27:  # ESC key
            self.back()
            return True

    def load_screen(self, screen_name: str) -> None:
        """Creates an instance of the screen object and adds it to the screen manager."""
        if not self.has_screen(screen_name):
            screen = self.screens_data.get(screen_name)
            if not screen:
                print(f"Screen {screen_name} not found in screens data.")
                return

            try:
                # Load KV file
                kv_path = screen.get("kv")
                if kv_path:
                    Builder.load_file(utils.abs_path(kv_path))

                # Import screen class dynamically
                module_name = screen.get("module")
                class_name = screen.get("class")

                if not module_name or not class_name:
                    print(
                        f"Missing 'module' or 'class' in screen data for {screen_name}."
                    )
                    return

                module = importlib.import_module(module_name)
                screen_class = getattr(module, class_name)
                screen_object = screen_class()
                screen_object.name = screen_name
                self.add_widget(screen_object)

            except (ImportError, AttributeError, FileNotFoundError) as e:
                print(f"Error loading screen {screen_name}: {e}")
