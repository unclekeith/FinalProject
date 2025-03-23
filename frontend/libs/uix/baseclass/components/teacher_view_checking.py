from kivy.lang import Builder
from kivy.properties import StringProperty
from kivymd.uix.list import MDListItem

KV = """
<TeacherCheckedItem>:
    radius: dp(5)
    theme_bg_color: "Custom"
    md_bg_color: root.background_color
    line_color: ("#008080")
    
    # on_release: root.parent.parent.parent.load_application_details(application=self.application)
    MDListItemHeadlineText:
        text: root.fullname
    
    MDListItemSupportingText:
        text: root.checked_status
        
    MDListItemTertiaryText:
        text: root.last_checking_info
        
    
     
"""

Builder.load_string(KV)


class TeacherCheckedItem(MDListItem):
    fullname = StringProperty()
    checked_status = StringProperty()
    last_checking_info = StringProperty()
    background_color = StringProperty("white")
