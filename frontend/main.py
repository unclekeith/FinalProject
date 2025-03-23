import asyncio

from kivy.core.window import Window
from kivy.metrics import dp
from kivy.utils import platform
from kivymd.app import MDApp
from libs.uix.root import Root

if platform != "android":
    Window.size = (dp(380), dp(720))


class MainApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        Window.keyboard_anim_args = {"d": 0.2, "t": "linear"}
        Window.softinput_mode = "below_target"

        self.title = "Embakwe Aziwe"
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Teal"

    def build(self):
        # Build root ScreenManager
        self.root = Root()

        self.root.push("welcome")


if __name__ == "__main__":
    asyncio.run(MainApp().async_run())
