from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.behaviors import ButtonBehavior
from kivymd.uix.boxlayout import MDBoxLayout

KV = """
<SubjectApplyListItem>:
    radius: dp(5)
    theme_bg_color: "Custom"
    md_bg_color: root.background_color
    line_color: 0, 1, 1, 1
    # size_hint_y: None
    # height: dp(60)
    adaptive_height: True
    padding: dp(10)
    
    on_release: print("I was Clicked")

    MDLabel:
        id: name_label
        text: root.subject_name
        pos_hint: {'center_y': 0.5}
    
    MDTextField:
        id: grade_text_field
        text: root.subject_grade
        pos_hint: {'center_y': 0.5}
        
    MDCheckbox:
        id: subject_checkbox
        pos_hint: {'center_y': 0.5}
"""

Builder.load_string(KV)


class SubjectApplyListItem(ButtonBehavior, MDBoxLayout):
    subject_name = StringProperty()
    subject_grade = StringProperty()
    background_color = StringProperty("grey")
