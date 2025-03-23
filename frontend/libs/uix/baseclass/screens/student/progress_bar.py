from kivy.lang import Builder
from kivymd.uix.button import MDIconButton
from kivymd.uix.screen import MDScreen
from kivy.clock import Clock
import random
from kivy.logger import Logger

class Progress(MDScreen):


    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Initializing capacities for dorms and classes
        self.dorm_capacity = {
            'Dorm A': 0,
            'Dorm B': 0,
            'Dorm C': 0,
            'Dorm D': 0
        }

        self.class_capacity = {
            'Sciences': 0,
            'Commercials': 0,
            'Arts 1': 0,
            'Arts 2': 0
        }

        self.max_dorm_capacity = 60
        self.max_class_capacity = 40

        # Initialize store_data dictionary
        self.store_data = {}

        self.athletic_houses = {
            'House 1': 0,
            'House 2': 0,
            'House 3': 0,
            'House 4': 0
        }

        self.school_classes = {
            'Sciences': 0,
            'Commercials': 0,
            'Arts 1': 0,
            'Arts 2': 0
        }

        self.subjects = {
            'Sciences': ['Physics', 'Chemistry', 'Biology', 'Math', 'Computer Science', 'Geography', 'Animal Science', 'Pure Maths'],
            'Commercials': ['Accounting', 'Economics', 'Business Studies', 'Mathematics', 'Statistics', 'Geography', 'Computer Science', 'Heritage'],
            'Arts 1': ['Philosophy', 'Sociology', 'Psychology', 'Literature', 'Art History', 'History', 'Heritage', 'FRS', 'Literature in English', 'Ndebele', 'Shona'],
            'Arts 2': ['Philosophy', 'Sociology', 'Psychology', 'Literature', 'Art History', 'History', 'Heritage', 'FRS', 'Literature in English', 'Ndebele', 'Shona']
        }

    def randomize_account(self, student_id):
        # Randomize the dormitory, athletic house, class, and subjects
        selected_dorm = self.select_dorm()
        selected_house = random.choice(list(self.athletic_houses.keys()))
        selected_class = self.select_class()
        
        # Randomize subjects based on the class, limit to 12 subjects maximum
        selected_subjects = random.sample(self.subjects[selected_class], min(12, len(self.subjects[selected_class])))

        # Save store_data to self.store_data
        self.store_data = {
            "selected_dorm": selected_dorm,
            "selected_house": selected_house,
            "selected_class": selected_class,
            "selected_subjects": selected_subjects
        }

        # Update capacities (increase the occupancy)
        self.dorm_capacity[selected_dorm] += 1
        self.class_capacity[selected_class] += 1

        # Save the store_data and updated capacities to shared data
        self.manager.set_shared_data("store_data", self.store_data)
        self.manager.set_shared_data("dorm_capacity", self.dorm_capacity)
        self.manager.set_shared_data("class_capacity", self.class_capacity)
        
        # Update UI
        self.update_account_info(selected_subjects)

        # Print the shared data for debugging
        Logger.info(f"Shared store_data data: {self.manager.get_shared_data('store_data')}")
        Logger.info(f"Updated dorm capacity: {self.manager.get_shared_data('dorm_capacity')}")
        Logger.info(f"Updated class capacity: {self.manager.get_shared_data('class_capacity')}")

    def select_dorm(self):
        available_dorms = [dorm for dorm, count in self.dorm_capacity.items() if count < self.max_dorm_capacity]
        if available_dorms:
            return random.choice(available_dorms)
        else:
            Logger.error("No available dorms")
            return None

    def select_class(self):
        available_classes = [cls for cls, count in self.class_capacity.items() if count < self.max_class_capacity]
        if available_classes:
            return random.choice(available_classes)
        else:
            Logger.error("No available classes")
            return None

    def update_account_info(self, selected_subjects):
        # Update dormitory, house, class, and subjects UI
        self.ids.dorm_label.text = f"Dormitory: {self.store_data['selected_dorm']} ({self.dorm_capacity[self.store_data['selected_dorm']]}/{self.max_dorm_capacity})"
        self.ids.house_label.text = f"Athletic House: {self.store_data['selected_house']}"
        self.ids.class_label.text = f"Class: {self.store_data['selected_class']}"

        subjects_text = "\n".join(selected_subjects)
        self.ids.subjects_label.text = f"Subjects Assigned:\n{subjects_text}"
    
        

    def on_enter(self):
        # Trigger account randomization once the screen is displayed
        self.update_user_level()

    def update_user_level(self):
        try:
            self.user = self.manager.get_shared_data("user")
            if self.user:
                self.academic_level = self.user.get("current_academic_level", "")
            else:
                Logger.warning("No user data found.")
        except Exception as e:
            Logger.error(f"Error updating user level: {e}")
            
            
        user_data = self.manager.get_shared_data("user")
        if user_data:
            user_id = user_data.get("id")  # Get the user ID from the shared datade
        else:
            return
        
        
        if self.academic_level == "A_LEVEL":
            self.manager.push_replacement("approval_for_ALevel")
        else:
            Clock.schedule_once(lambda dt: self.randomize_account(student_id=user_id), 0.1)
        
        
    def finish_up(self):
    # Navigate directly to student_dashboard
        self.manager.push("student_dashboard")