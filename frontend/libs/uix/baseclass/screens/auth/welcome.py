import logging

from kivy.animation import Animation
from kivy.clock import Clock  # noqa: F401
from kivy.utils import platform
from kivymd.uix.screen import MDScreen
from libs.applibs.generated_connection_manager import AuthRoutes, CoreRoutes


class WelcomeScreen(MDScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.health_schedule = None
        self.is_online = None
        self.animation = None  # To store the current animation
        # self.connection_manager = GeneratedConnectionManager("http://127.0.0.1:8000")

    def on_enter(self):
        self.healthcheck()
        self.health_schedule = Clock.schedule_interval(self.healthcheck, 10)

        """Called when the screen is entered. Requests necessary permissions on Android."""
        if platform == "android":
            logging.info("Requesting Android permissions.")
            self.request_android_permissions()

    def on_leave(self):
        self.health_schedule.cancel()
        if self.animation:
            self.animation.stop(self.ids.status_label)  # Stop the ongoing animation
            self.ids.status_label.text = ""  # Clear text if needed
            self.animation = None  # Clear the animation reference

    def healthcheck(self, *args, **kwargs):
        try:
            response = CoreRoutes(
                client=self.manager.connection_client
            ).get_healthcheck()
            online = response.status_code == 200
        except Exception as e:
            print(f"Health check failed: {e}")
            online = False

        if online != self.is_online:
            # If the online status has changed, update the animation
            if online:
                self.animate_online()
            else:
                self.animate_offline()

        self.is_online = online

    def animate_online(self, *args, **kwargs):
        if self.animation:
            self.animation.stop(self.ids.status_label)  # Stop any existing animation

        self.animation = (
            Animation(font_size=20, duration=0.2)
            + Animation(font_size=24, duration=0.2)
            + Animation(font_size=20, duration=0.2)
        )
        self.animation.repeat = True  # Make the animation loop indefinitely

        self.animation.start(self.ids.status_label)
        self.ids.status_label.text_color = "#00FF00"
        self.ids.status_label.text = "Online"
        self.ids.one.disabled = False
        self.ids.two.disabled = False

    def animate_offline(self, *args, **kwargs):
        if self.animation:
            self.animation.stop(self.ids.status_label)  # Stop any existing animation

        self.animation = (
            Animation(font_size=20, duration=0.2)
            + Animation(font_size=24, duration=0.2)
            + Animation(font_size=20, duration=0.2)
        )
        self.animation.repeat = True  # Make the animation loop indefinitely

        self.animation.start(self.ids.status_label)
        self.ids.status_label.text_color = "#FF0000"
        self.ids.status_label.text = "Please connect to a network"
        self.ids.one.disabled = True
        self.ids.two.disabled = True

    def stop_animation(self, instance):
        if self.animation:
            self.animation.stop(self.ids.status_label)
            self.ids.status_label.text = ""  # Clear text if needed
            self.animation = None  # Clear the animation reference

    def move_login(self):
        if not self.ids.one.disabled:
            self.manager.push("login")

    def move_register(self):
        if not self.ids.one.disabled:
            self.manager.push("register")

    def log_out(self, **kwargs):
        AuthRoutes(client=self.manager.connection_client).post_logout()
        self.manager.push_replacement("login")

    def request_android_permissions(self):
        """
        Requests necessary Android permissions required to make a phone call.
        These permissions include external storage, camera, and call permissions.
        """
        try:
            from android.permissions import Permission, request_permissions

            # Callback function to handle the results of the permission request
            def callback(permissions, results):
                for permission, result in zip(permissions, results):
                    if result:
                        logging.info(f"Permission granted: {permission}")
                    else:
                        logging.warning(f"Permission denied: {permission}")
                        # Optionally, notify the user that certain features won't work

            # Request permissions necessary for phone calls
            request_permissions(
                [
                    Permission.WRITE_EXTERNAL_STORAGE,
                    Permission.READ_EXTERNAL_STORAGE,
                    Permission.CAMERA,
                    Permission.VIBRATE,
                    Permission.ACCESS_FINE_LOCATION,
                    Permission.ACCESS_COARSE_LOCATION,
                    Permission.POST_NOTIFICATIONS,
                    Permission.READ_CALENDAR,
                    Permission.USE_FINGERPRINT,
                ],
                callback,
            )
        except ImportError as e:
            logging.error(f"Android permissions module not found: {e}")
        except Exception as e:
            logging.error(f"Error while requesting permissions: {e}")
