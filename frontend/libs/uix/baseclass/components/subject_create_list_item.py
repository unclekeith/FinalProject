from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.behaviors import ButtonBehavior
from kivymd.uix.boxlayout import MDBoxLayout

KV = """
<SubjectCreateListItem>:
    radius: dp(5)
    theme_bg_color: "Custom"
    md_bg_color: root.background_color
    adaptive_height: True
    padding: dp(10)
    
    MDLabel:
        id: name_label
        text: root.subject_name
    
    MDTextField:
        id: grade_text_field
        text: root.subject_grade
"""

Builder.load_string(KV)


class SubjectCreateListItem(ButtonBehavior, MDBoxLayout):
    subject_name = StringProperty()
    subject_grade = StringProperty()
    background_color = StringProperty("grey")
