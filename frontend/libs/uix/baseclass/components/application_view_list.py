from kivy.lang import Builder
from kivy.properties import DictProperty, StringProperty
from kivy.uix.behaviors import ButtonBehavior
from kivymd.uix.boxlayout import MDBoxLayout

KV = """
<ApplicationViewListItem>:
    radius: dp(5)
    theme_bg_color: "Custom"
    md_bg_color: root.background_color
    line_color: 0, 1, 1, 1
    size_hint_y: None
    height: dp(60)
    padding: dp(10)
    
    on_release: root.parent.parent.parent.load_application_details(application=self.application)

    MDLabel:
        id: name_label
        text: root.applicant_name
    
    MDLabel:
        id: status_label
        text: root.status
"""

Builder.load_string(KV)


class ApplicationViewListItem(ButtonBehavior, MDBoxLayout):
    status = StringProperty()
    applicant_name = StringProperty()
    background_color = StringProperty("white")
    application = DictProperty()
