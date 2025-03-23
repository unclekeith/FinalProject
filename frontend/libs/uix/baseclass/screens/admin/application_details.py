from kivy.uix.accordion import ObjectProperty
from kivymd.uix.screen import MDScreen
from kivy.properties import ListProperty,ObjectProperty
from libs.applibs.generated_connection_manager import StudentsubjectsRoutes
from libs.uix.baseclass.components.subject_view_list import SubjectListItehm
from kivymd.uix.label import MDLabel


class ApplicationDetailsScreen(MDScreen):
    subjects = []

    def on_pre_enter(self):
        # Fetch and populate subjects when the screen is about to be entered
        self.get_all_my_subjects()

    def get_all_my_subjects(self):
        try:
            response = StudentsubjectsRoutes(
                client=self.manager.connection_client
            ).get_student_subjects()

            # Check if the request was successful
            if response.status_code == 200:
                student_subjects = response.json()
                print(student_subjects)
                self.subjects = student_subjects  # Update the subjects list

                # Set the subjects to the shared data (optional)
                self.manager.set_shared_data("student_subjects", student_subjects)

                # Populate the UI after receiving subjects
                self.populate_subjects_ui()
                print(student_subjects)
            else:
                print(f"Error fetching subjects: {response.status_code}")

        except Exception as e:
            print(f"Error fetching subjects: {e}")

    def populate_subjects_ui(self):
        # Clear any existing subjects
        self.ids.subjects.clear_widgets()

        # Iterate through all subjects and display them in the UI
        for student_subjects in self.subjects:
            self.ids.subjects.add_widget(
                SubjectListItehm(
                    subject_name=student_subjects.get(
                        "name", "N/A"
                    ),  # Assuming 'name' is a key in the response
                    subject_grade=student_subjects.get(
                        "grade", "N/A"
                    ),  # Assuming 'grade' is the symbol for the subject
                )
            )
