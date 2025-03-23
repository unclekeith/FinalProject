from kivy.lang import Builder
from kivy.properties import StringProperty
from kivymd.uix.list import MDListItem

KV = """
<UserViewListItem>:
    radius: dp(5)
    theme_bg_color: "Custom"
    md_bg_color: root.background_color
    line_color: ("#008080")
    
    # on_release: root.parent.parent.parent.load_application_details(application=self.application)
    MDListItemHeadlineText:
        text: root.fullname
    
    MDListItemSupportingText:
        text: root.email
        
    MDListItemTertiaryText:
        text: root.phone_number
    
    
"""

Builder.load_string(KV)


class UserViewListItem(MDListItem):
    fullname = StringProperty()
    email = StringProperty()
    phone_number = StringProperty()
    background_color = StringProperty("white")
