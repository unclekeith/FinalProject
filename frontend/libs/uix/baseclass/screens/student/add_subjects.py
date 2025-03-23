from kivymd.uix.screen import MDScreen
from libs.applibs.generated_connection_manager import (  # noqa: F401
    StudentsubjectsRoutes,
    SubjectsRoutes,
    ApplicationsRoutes,
)
from kivy.metrics import dp
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from libs.uix.baseclass.components.subject_create_list_item import SubjectCreateListItem
from kivy.logger import Logger
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarSupportingText
from kivy.clock import Clock
class AddSubjectsScreen(MDScreen):
    combination = ""

    def on_pre_enter(self):
        # Fetch the combination from shared data
        self.combination = str(self.manager.get_shared_data("combination") or "")
        print(f"Combination: {self.combination}")  # For debugging
        

        # Ensure that combination is a valid string (non-empty and non-None)
        if not self.combination or not isinstance(self.combination, str):
            # Set to a default value if it's invalid or empty
            self.combination = "O Level"  # You can change this to any default value you prefer

        print(f"Combination: {self.combination}")  # For debugging

        # Fetch and populate subjects when the screen is about to be entered
        self.get_all_subjects()

    def get_all_subjects(self):
        try:
            response = SubjectsRoutes(client=self.manager.connection_client).get_subjects()

            # Check if the request was successful
            if response.status_code == 200:
                student_subjects = response.json()
                self.subjects = student_subjects  # Update the subjects list

                # Set the subjects to the shared data (optional)
                self.manager.set_shared_data("student_subjects", student_subjects)

                # Populate the UI after receiving subjects
                self.populate_subjects_ui()
            else:
                print(f"Error fetching subjects: {response.status_code}")

        except Exception as e:
            print(f"Error fetching subjects: {e}")

    def populate_subjects_ui(self):
        # Clear any existing subjects
        self.ids.subjects.clear_widgets()

        # Iterate through all subjects and display them in the UI
        for subject in self.subjects:
            self.ids.subjects.add_widget(
                SubjectCreateListItem(
                    subject_name=subject.get("name", "N/A"),  # Assuming 'name' is a key in the response
                    subject_grade=subject.get("grade", "N/A"),  # Assuming 'grade' is the symbol for the subject
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
                    
            response = StudentsubjectsRoutes(client=self.manager.connection_client).post_bulk_add_student_subject(
                json=valid_subjects
            )  # With a list of student subjects to add

            if response.status_code == 200:
                print("Sent the subjects")
                # Proceed to send the application
            else:
                Logger.error(f"Error sending subjects: {response.status_code}")

            # Send combination and subjects to the server
            response = ApplicationsRoutes(client=self.manager.connection_client).post_apply(
                json={
                    "combination": self.combination,  # Use the combination value set earlier
                    "subjects": valid_subjects,
                }
            )
            if response.status_code == 200:
                self.succesfully_sent()
                Logger.info("Application Sent Successfully!")
                self.manager.push("my_subjects")
                
            else:
                Logger.error(
                    f"Error in sending application: {response.status_code} - {response.json().get('detail', 'Unknown error')}"
                )
        except Exception as e:
            Logger.error(f"Error in get_subjects_with_symbols: {e}")
    
    
    def succesfully_sent(self):
        MDSnackbar(
            MDSnackbarSupportingText(
                text=" Application Sent Successfully!",
            ),
            y=dp(24),
            orientation="vertical",
            pos_hint={"center_x": 0.5},
            size_hint_x=0.9,
            # background_color="white",
        ).open()

    