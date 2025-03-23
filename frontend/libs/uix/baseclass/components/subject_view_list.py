from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.behaviors import ButtonBehavior
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel  # noqa: F401

KV = """
<SubjectListItehm>:
    radius: dp(5)
    theme_bg_color: "Custom"
    md_bg_color: root.background_color
    line_color: 0, 1, 1, 1
    size_hint_y: None
    height: dp(60)
    padding: dp(10)
    
    MDLabel:
        text: root.subject_name
    
    MDLabel:
        text: root.grade
"""


Builder.load_string(KV)

KV = """
<SubjectListItem>:
    radius: dp(5)
    theme_bg_color: "Custom"
    md_bg_color: root.background_color
    line_color: 0, 1, 1, 1
    size_hint_y: None
    height: dp(60)
    padding: dp(10)
    spacing: '17dp'
    
"""


Builder.load_string(KV)



class SubjectListItehm(ButtonBehavior, MDBoxLayout):
    subject_name = StringProperty()
    grade = StringProperty()
    background_color = StringProperty("grey")


class SubjectListItem(MDBoxLayout):
    background_color = StringProperty("grey")
    
    def __init__(self, teacher_account, message_content, timestamp, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        
        
        # Create widgets for teacher name, message, and timestamp
        self.add_widget(
            MDLabel(text=f"Teacher ID: {teacher_account}", theme_text_color="Secondary")
        )
        self.add_widget(
            MDLabel(text=f"Message: {message_content}", theme_text_color="Secondary")
        )
        self.add_widget(
            MDLabel(text=f"Timestamp: {timestamp}", theme_text_color="Secondary")
        )
