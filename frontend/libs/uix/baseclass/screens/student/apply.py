from kivy.clock import Clock
from kivy.metrics import dp
from kivymd.uix.button import MDButton, MDButtonIcon, MDButtonText, MDIconButton
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from libs.applibs.generated_connection_manager import (
    ApplicationsRoutes,
    StudentsubjectsRoutes
)
from libs.uix.baseclass.components.subject_apply_list import SubjectApplyListItem
from kivy.properties import ObjectProperty
from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import (
    MDDialog,
    MDDialogButtonContainer,
    MDDialogContentContainer,
)
from kivy.uix.widget import Widget
from kivymd.uix.progressindicator import MDCircularProgressIndicator
from kivy.logger import Logger

class ApplyScreen(MDScreen):
    transition_done = False  # Flag to prevent repeated transitions
    academic_level = ObjectProperty()
    subjects = []
    application_sent = False  # Flag to track if the application has been sent
    PROGRESS_INDICATOR_SIZE = ("120dp", "120dp")
    BUTTON_RADIUS = 42
    BUTTON_COLOR = "green"
    ICON_COLOR = "white"
    ICON_SIZE = "28sp"
    PROGRESS_DURATION = 10
    STATUS_CHECK_INTERVAL = 2

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.application_status_displayed = False
        self.application_check_event = None
        self.combination_field = None
        self.combination = None

    def update_user_level(self):
        try:
            self.user = self.manager.get_shared_data("user")
            if self.user:
                self.academic_level = self.user.get("current_academic_level", "")
                Logger.info(f"Academic Level: {self.academic_level}")
            else:
                Logger.warning("No user data found.")
        except Exception as e:
            Logger.error(f"Error updating user level: {e}")

    def on_pre_enter(self):
        self.ids.check.clear_widgets()
        self.get_user_application()
        self.manager.set_shared_data("combination", self.combination)
        Clock.schedule_interval(self.get_user_application, 5)

    def on_enter(self):
        self.ids.check.clear_widgets()
        self.get_user_application()
        self.update_user_level()

        # Only continue to show application flow if application is not sent
        if not self.application_sent:
            if self.academic_level == "A_LEVEL":
                self.application_check_event = Clock.schedule_interval(
                    self.check_for_application_updates, self.STATUS_CHECK_INTERVAL
                )
                self.get_user_application()
                self.combination_dialog()
            else:
                self.application_check_event = Clock.schedule_interval(
                    self.check_for_application_updates, self.STATUS_CHECK_INTERVAL
                )
                self.get_user_application()

    def combination_dialog(self):
        try:
            self.combination_field = MDTextField(
                hint_text="Enter your combination (e.g., Sciences, Arts)",
                pos_hint={"center_y": 0.5},
            )

            dialog = MDDialog(
                MDDialogContentContainer(
                    MDBoxLayout(
                        MDLabel(
                            markup=True,
                            text="[size=16sp][b] Enter Your Combination:[/b][/size]",
                            size_hint_x=None,
                            width=dp(150),
                            valign="middle",
                            adaptive_height=True,
                            pos_hint={"center_y": 0.5},
                        ),
                        self.combination_field,  # Attach the text field for event name
                        adaptive_height=True,
                    ),
                    orientation="vertical",
                    spacing=10,
                ),
                MDDialogButtonContainer(
                    Widget(),
                    MDButton(
                        MDButtonText(text="Cancel"),
                        style="text",
                        on_release=lambda x: dialog.dismiss(),
                    ),
                    MDButton(
                        MDButtonText(text="Next"),
                        style="text",
                        on_release=lambda x: self.create_new_event(dialog)
                    ),
                    spacing="8dp",
                ),
                size_hint_x=None,
                size_hint_y=None,
                width=350,
                height=500,
            )
            dialog.open()
        except Exception as e:
            Logger.error(f"Error opening combination dialog: {e}")

    def create_new_event(self, dialog):
        try:
            combination_input = self.combination_field.text.strip()
            if combination_input:
                self.combination = combination_input
                dialog.dismiss()
                Logger.info(f"Combination entered: {self.combination}")

                # Fetch subjects and populate the UI for user selection
                self.get_user_subjects()
            else:
                Logger.warning("Combination cannot be empty!")
        except Exception as e:
            Logger.error(f"Error creating new event: {e}")


    def apply(self, *args, **kwargs):
        
        # Proceed to send the combination and selected subjects
        # self.get_subjects_with_symbols()
        # self.manager.push("my_subjects")
        self.get_user_subjects()

    def on_leave(self):
        if self.application_check_event:
            Clock.unschedule(self.application_check_event)

    def check_for_application_updates(self, dt):
        self.get_user_application()

    def get_user_application(self, dt=None):
        user_application = self.manager.get_shared_data("user").get("application")

        if len(user_application) > 0:
            user_application = user_application[0]
            application_status = user_application.get("status")
            color = ""

            # Clear previous status if already displayed
            if self.application_status_displayed:
                self.ids.check.clear_widgets()
                self.application_status_displayed = False

            # Check and update status based on application status
            if application_status == "SENT":
                color = "orange"
                self.sent()
                self.application_status_displayed = True                
                self.application_sent = True  # Mark as sent
                self.hide_apply_button()  # Hide the apply button when already sent

            elif application_status == "PENDING":
                color = (0.8, 0.3, 0.8, 5)
                self.pending()
                self.application_status_displayed = True

            elif application_status == "APPROVED":
                color = "green"
                self.show_check_icon()
                self.application_status_displayed = True
                self.application_sent = True  
                if not self.transition_done:
                    Clock.schedule_once(self.switch_to_next_screen, 5)

                

            elif application_status == "REJECTED":
                color = "red"
                self.application_status_displayed = True
                self.application_sent = True  
                if not self.transition_done:
                    Clock.schedule_once(self.switch_to_rejected_screen, 5)

            # Add card to show the current status
            self.add_widget(
                MDCard(
                    MDLabel(text="Application Status"),
                    MDLabel(text=f"{application_status}"),
                    orientation="horizontal",
                    pos_hint={"center_x": 0.5, "center_y": 0.4},
                    size_hint=(None, None),
                    theme_bg_color="Custom",
                    md_bg_color=color,
                    size_hint_x=0.7,
                    size_hint_y=0.08,
                    padding=(dp(20), 0, 0, 0),
                )
            )
        else:
            self.populate_subjects_ui()

            

    # Other methods remain unchanged (populate_subjects_ui, apply, show_check_icon, etc.)

    def get_user_subjects(self):
        try:
            self.populate_subjects_ui()
            self.manager.push("my_subjects")
            response = StudentsubjectsRoutes(
                client=self.manager.connection_client
            ).get_student_subjects()

            # Check if the request was successful
            if response.status_code == 200:
                student_subjects = response.json()
                self.subjects = student_subjects  # Update the subjects list

                # Set the subjects to the shared data (optional)
                self.manager.set_shared_data("student_subjects", student_subjects)

                # Populate the UI after receiving subjects
                
            else:
                print(f"Error fetching subjects: {response.status_code}")

        except Exception as e:
            print(f"Error fetching subjects: {e}")

    def hide_apply_button(self):
        """Disable the apply button if the application has been sent."""
        # Fetch the apply_button safely using 'get'
        apply_button = self.ids.get('apply_button')

        if apply_button:
            # Disable the button interaction
            apply_button.disabled = True  # This will make it visually disabled
            apply_button.opacity = 0.3  # Optionally change the opacity for visual feedback
            
            # Remove the on_release callback to ensure it's not clickable
            apply_button.on_release = None


    def populate_subjects_ui(self):
        # Clear any existing subjects
        self.ids.subjects.clear_widgets()

        # Iterate through all subjects and display them in the UI
        for subject in self.subjects:
            self.ids.subjects.add_widget(
                SubjectApplyListItem(
                    subject_name=subject.get(
                        "name", "N/A"
                    ),  # Assuming 'name' is a key in the response
                    subject_grade=subject.get(
                        "grade", "N/A"
                    ),  # Assuming 'grade' is the symbol for the subject
                )
            )

        if not self.application_sent:  # Only add the apply button if the application isn't sent
            self.add_widget(
                MDButton(
                    MDButtonText(text="Apply"),
                    MDButtonIcon(icon="check-decagram"),
                    on_release=self.apply,
                    pos_hint={"center_x": 0.5, "center_y": 0.1},
                    radius=dp(0),
                    id="apply_button",  # Assign an id for easy reference
                )
            )

    def get_subjects_with_symbols(self):
        try:
            # Collect all subjects and their grades
            all_subjects = self.ids.subjects.children
            valid_subjects = []

            for subject_widget in all_subjects:
                subject_name = subject_widget.subject_name
                subject_grade = subject_widget.ids.grade_text_field.text.upper()

                if subject_grade == "X" or len(subject_grade) > 1:
                    Logger.warning(f"Invalid grade for subject '{subject_name}': {subject_grade}")
                else:
                    valid_subjects.append({"name": subject_name, "grade": subject_grade})
                    
            response = StudentsubjectsRoutes(
                client=self.manager.connection_client
            ).post_bulk_add_student_subject(
                json=valid_subjects
            )  # With a list of student subjects to add

            if response.status_code == 200:
                print("sent the subjects")
                # change to the

            # Send combination and subjects to the server
            response = ApplicationsRoutes(client=self.manager.connection_client).post_apply(
                json={
                    "combination": self.combination,
                    "subjects": valid_subjects,
                }
            )
            if response.status_code == 200:
                Logger.info("Application Sent Successfully!")
            else:
                Logger.error(
                    f"Error in sending application: {response.status_code} - {response.json().get('detail', 'Unknown error')}"
                )
        except Exception as e:
            Logger.error(f"Error in get_subjects_with_symbols: {e}")
        
        

    
    def show_check_icon(self, dt=None):
        check_button = MDIconButton(
            icon="check",
            style="tonal",
            theme_font_size="Custom",
            font_size=self.ICON_SIZE,
            radius=[self.BUTTON_RADIUS],
            size_hint=(None, None),
            size=self.PROGRESS_INDICATOR_SIZE,
            pos_hint={"center_x": 0.5, "center_y": 0.6},
            # theme_color=self.BUTTON_COLOR,
        )
        self.ids.check.add_widget(check_button)

    def switch_to_next_screen(self, dt=None):
        if not self.transition_done:  # Check if transition is already done
            Logger.info("Switching to the next screen.")
            self.manager.push("progress")
            self.transition_done = True  # Set the flag to True to prevent further transitions
        else:
            Logger.info("Transition already done, skipping.")
            
    def switch_to_rejected_screen(self, dt=None):
        if not self.transition_done:  # Check if transition is already done
            Logger.info("Switching to the reject screen.")
            self.manager.push("rejected_message")
            self.transition_done = True  # Set the flag to True to prevent further transitions
        else:
            Logger.info("Transition already done, skipping.")

    def pending(self, dt=None):
        # Create and add the check icon
        button = MDCircularProgressIndicator(
            size_hint=(None, None),
            size=(48, 48),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            color=(0.8, 0.3, 0.8, 5),
        )
        self.ids.check.add_widget(button)

    def sent(self, dt=None):
        # Create and add the check icon
        sent = MDCircularProgressIndicator(
            size_hint=(None, None),
            size=(48, 48),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            color="orange",
        )
        self.ids.check.add_widget(sent)
